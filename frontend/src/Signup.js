// src/Signup.js
import React, { useState } from 'react';
import axios from 'axios';

const Signup = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState(''); // Added password confirmation
    const [firstName, setFirstName] = useState(''); // Added first name
    const [lastName, setLastName] = useState(''); // Added last name

    const handleSignup = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/accounts/register/', {
                username,
                email,
                password,
                password2, // Include password2 in the request
                first_name: firstName, // Include first name in the request
                last_name: lastName, // Include last name in the request
            });
            // Store the token in local storage
            localStorage.setItem('token', response.data.access);
            alert('User created successfully!');
        } catch (error) {
            console.error('Error signing up:', error);
            if (error.response) {
                console.error('Response data:', error.response.data);
                alert(`Failed to create user: ${error.response.data.detail || error.response.data}`);
            } else {
                alert('Failed to create user: Network error');
            }
        }
    };

    return (
        <div className="container mt-4">
            <h2>Sign Up</h2>
            <form onSubmit={handleSignup}>
                <div className="form-group">
                    <label htmlFor="firstName">First Name</label>
                    <input type="text" className="form-control" id="firstName" placeholder="Enter first name" value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label htmlFor="lastName">Last Name</label>
                    <input type="text" className="form-control" id="lastName" placeholder="Enter last name" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input type="text" className="form-control" id="username" placeholder="Enter username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input type="email" className="form-control" id="email" placeholder="Enter email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input type="password" className="form-control" id="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label htmlFor="password2">Confirm Password</label>
                    <input type="password" className="form-control" id="password2" placeholder="Confirm Password" value={password2} onChange={(e) => setPassword2(e.target.value)} required />
                </div>
                <button type="submit" className="btn btn-primary">Sign Up</button>
            </form>
        </div>
    );
};

export default Signup;