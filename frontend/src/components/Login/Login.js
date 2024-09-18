import React from 'react';
import './Login.css';  

function Login() {
  return (
    <div className="login-container">
      <h1>Login</h1>
      <form>
        <label>Email</label>
        <input type="email" />
        <label>Password</label>
        <input type="password" />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;
