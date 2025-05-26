describe('Homepage', () => {
  it('successfully loads', () => {
    cy.visit('/') // visits baseUrl

    // Check that some text or element exists, adjust to your app
    cy.contains('Welcome').should('exist')
  })
})
