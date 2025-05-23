describe('Basic Vue App Test', () => {
  it('Visits the homepage and checks for Vue text', () => {
    cy.visit('/')
    cy.contains('h1', 'Vue')
  })
})
