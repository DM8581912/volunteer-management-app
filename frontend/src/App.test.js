import { render, screen } from '@testing-library/react';
import App from './App';

test('redirects to the login page by default', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
});
