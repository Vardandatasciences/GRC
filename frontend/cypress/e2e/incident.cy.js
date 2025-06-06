describe('Incident Page Smoke Test', () => {
  it('should load the incident module page', () => {
    cy.visit('http://localhost:8082') // Update this path if your app routes to /incident
    cy.contains('Incident').should('exist') // Adjust based on actual heading
  });
});
