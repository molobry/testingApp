Feature: User Login
  As a user
  I want to login to the application
  So that I can access my account

  Background:
    Given I navigate to "https://example.com/login"

  @smoke @login
  Scenario: Successful login
    When I type "john@example.com" into "email field"
    And I type "password123" into "password field"
    And I click "Login button"
    Then I should see "Welcome back, John!"

  @regression
  Scenario: Failed login
    When I type "wrong@example.com" into "email field"
    And I type "wrongpassword" into "password field"
    And I click "Login button"
    Then I should see "Invalid credentials"

  Scenario: Password reset
    When I click "Forgot password link"
    And I type "john@example.com" into "reset email field"
    And I click "Send reset link"
    Then I should see "Password reset email sent"