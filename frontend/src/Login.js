// src/Login.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/accounts/login/', {
                email,
                password,
            });
            
            // Store the tokens in localStorage
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);
            
            // Set the default Authorization header for future requests
            axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
            
            alert('Logged in successfully!');
            navigate('/'); // Redirect to home page
        } catch (error) {
            console.error('Error logging in:', error);
            if (error.response) {
                console.error('Response data:', error.response.data);
                alert(`Failed to log in: ${error.response.data.detail || JSON.stringify(error.response.data)}`);
            } else {
                alert('Failed to log in: Network error');
            }
        }
    };

    return (
        <div className="container mt-4">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        className="form-control"
                        id="email"
                        placeholder="Enter email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        className="form-control"
                        id="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary">Log In</button>
            </form>
        </div>
    );
};

export default Login;