!pip -q install --upgrade pip
!pip -q install pymupdf==1.23.6 pdfplumber sentencepiece pandas openpyxl tqdm
# ▸ Run this *once* in a fresh cell
!pip install -U -q transformers==4.40.1 accelerate bitsandbytes==0.42.0
#  - v4.40.1 (or newer) contains get_loading_attributes
#  - bitsandbytes 0.42.0 is compiled against CUDA 11.x & 12.x and matches HF 4-bit API

!pip -q install -U "transformers>=4.41.0" accelerate bitsandbytes sentencepiece


import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

MODEL_ID = "numind/NuExtract-1.5"

def load_nuextract_gpu(model_id: str = MODEL_ID):
    """Load full-precision Phi-3 fine-tune on GPU."""
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    return tok, model


def load_nuextract_cpu_4bit(model_id: str = MODEL_ID):
    """Load 4-bit quantised NuExtract so it fits in CPU / low-VRAM GPUs."""
    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        quantization_config=bnb_cfg,
        trust_remote_code=True,
    )
    return tok, model

import transformers, bitsandbytes, accelerate, torch
print("Transformers:", transformers.__version__)
print("BitsAndBytes :", bitsandbytes.__version__)
print("Accelerate   :", accelerate.__version__)
# > make sure transformers ≥ 4.39 and bitsandbytes ≥ 0.41.x
!pip install -q huggingface_hub  # if not already

from huggingface_hub import login
login("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")   # paste your read token

tok, model = load_nuextract_gpu()        # or load_nuextract_cpu_4bit()
print("Loaded NuExtract ✔")


import re
import fitz  # PyMuPDF
import pandas as pd
from tqdm.auto import tqdm

def extract_text_blocks(pdf_path: str) -> list[str]:
    """
    Returns a list where each element is the text of one page.
    For compliance docs, page-level chunks are usually OK;
    refine if you need finer section splitting.
    """
    text_pages = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text_pages.append(page.get_text("text"))
    return text_pages


def chunk_by_tokens(text: str, tokenizer, max_tokens: int = 3500) -> list[str]:
    """
    Split long strings so they don't exceed the model context window (≈4096 for Llama-2).
    Uses tokenizer length as an approximation.
    """
    words = text.split()
    chunks, current = [], []
    for w in words:
        current.append(w)
        if len(tokenizer(" ".join(current)).input_ids) > max_tokens:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def llm_extract(chunk: str, tokenizer, model, device: str = None) -> str:
    """
    Runs a single prompt and returns raw model output (string).
    """
    prompt = (
        "You are a strict compliance data extractor.\n"
        "TASK: From the text delimited by <DOC></DOC>, list every policy, its sub-policy "
        "and the compliance reference exactly as written.\n"
        "Return ONLY comma-separated lines in the format:\n"
        "Policy, Sub-Policy, Compliance\n"
        "<DOC>\n"
        f"{chunk}\n"
        "</DOC>"
    )

    inputs = tokenizer(prompt, return_tensors="pt")
    if device:
        inputs = {k: v.to(device) for k, v in inputs.items()}

    output_ids = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.0,
        do_sample=False
    )
    generated = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    # Keep only the part AFTER the prompt for cleanliness
    return generated.split("</DOC>")[-1].strip()



def pdf_to_excel(
    pdf_path: str,
    excel_path: str = "ComplianceExtraction.xlsx",
    use_gpu: bool = True,
):
    """
    High-level wrapper: extracts (Policy, Sub-Policy, Compliance) triples
    from an ISO/NIST PDF and writes an Excel file.
    """
    # ---- 5.1 Load model (choose GPU or CPU path) ---------------------------
    if use_gpu and torch.cuda.is_available():
        tokenizer, model = load_nuextract_gpu()
        device = model.device
        print("🔧 Using GPU path")
    else:
        tokenizer, model = load_nuextract_cpu_4bit()
        device = model.device
        print("🔧 Using CPU / 4-bit path")

    # ---- 5.2 Parse PDF -----------------------------------------------------
    pages = extract_text_blocks(pdf_path)

    # ---- 5.3 Iterate & query LLM ------------------------------------------
    records = []
    for page_text in tqdm(pages, desc="Processing pages"):
        # Further split if page is too long
        for chunk in chunk_by_tokens(page_text, tokenizer):
            raw = llm_extract(chunk, tokenizer, model, device)
            # Parse CSV-like lines
            for line in raw.splitlines():
                # Expect exactly 3 comma-separated fields
                parts = [p.strip() for p in line.split(",")]
                if len(parts) == 3:
                    records.append(parts)

    # ---- 5.4 Save to Excel -------------------------------------------------
    if records:
        df = pd.DataFrame(records, columns=["Policy", "Sub-Policy", "Compliance"])
        df.to_excel(excel_path, index=False)
        print(f"✅ Saved {len(df)} rows → {excel_path}")
    else:
        print("⚠️  No records extracted; check parsing or prompt.")


# Case 1: run with GPU (if Colab GPU runtime enabled)
# pdf_to_excel("/content/NIST.SP.800-53r5.pdf", "iso_extract.xlsx", use_gpu=True)

# # Case 2: force CPU / low-VRAM mode (loads 4-bit GPTQ)
pdf_to_excel("/content/NIST_SP800-53.pdf", "nist_extract.xlsx", use_gpu=False)