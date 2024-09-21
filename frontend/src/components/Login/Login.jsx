import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; 
import styles from "./Login.module.css";  
const Login = () => {
  const [email, setEmail] = useState('testuser@example.com');
  const [password, setPassword] = useState('password123');
  const navigate = useNavigate(); 

    const handleSubmit = (e) => {
    e.preventDefault();

   if (email === 'testuser@example.com' && password === 'password123') {
      alert('Login successful!');
      navigate('/profile'); 
    } else {
      alert('Invalid login credentials');
    }
  };

  return (
    <div className={styles.loginContainer}> 
      <h2 className={styles.heading}>Login</h2> 
      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}> 
          <label>Email</label>
          {/* Bind input value to state */}
          <input 
            type="email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            className={styles.input} 
          />
        </div>
        
        <div className={styles.formGroup}> 
          <label>Password</label>
          {/* Bind input value to state */}
          <input 
            type="password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            className={styles.input} 
          />
        </div>
        
        <button type="submit" className={styles.button}>Login</button> 
      </form>
    </div>
  );
};

export default Login;
