// src/Signup.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Signup.css';

const Signup = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password2: '',
        first_name: '',
        last_name: ''
    });
    const [errors, setErrors] = useState({});

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prevErrors => ({
                ...prevErrors,
                [name]: null
            }));
        }
    };

    const handleSignup = async (e) => {
        e.preventDefault();
        setErrors({});

        try {
            const response = await axios.post('http://127.0.0.1:8000/api/accounts/register/', formData);
            
            // Store tokens in localStorage
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);
            localStorage.setItem('user_email', formData.email);
            
            // Show success message and redirect
            alert('Account created successfully!');
            navigate('/');
        } catch (error) {
            console.error('Error signing up:', error);
            if (error.response?.data) {
                // Handle validation errors
                setErrors(error.response.data);
                
                // Create a user-friendly error message
                const errorMessages = [];
                Object.entries(error.response.data).forEach(([field, messages]) => {
                    if (Array.isArray(messages)) {
                        errorMessages.push(`${field}: ${messages.join(', ')}`);
                    } else if (typeof messages === 'string') {
                        errorMessages.push(`${field}: ${messages}`);
                    }
                });
                
                if (errorMessages.length > 0) {
                    alert(errorMessages.join('\n'));
                }
            } else {
                alert('An error occurred during signup. Please try again.');
            }
        }
    };

    return (
        <div className="signup-container">
            <h2>Sign Up</h2>
            <form onSubmit={handleSignup} className="signup-form">
                <div className="form-group">
                    <label htmlFor="first_name">First Name</label>
                    <input
                        type="text"
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                        className={`form-control ${errors.first_name ? 'is-invalid' : ''}`}
                        required
                    />
                    {errors.first_name && <div className="invalid-feedback">{errors.first_name}</div>}
                </div>

                <div className="form-group">
                    <label htmlFor="last_name">Last Name</label>
                    <input
                        type="text"
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        className={`form-control ${errors.last_name ? 'is-invalid' : ''}`}
                        required
                    />
                    {errors.last_name && <div className="invalid-feedback">{errors.last_name}</div>}
                </div>

                <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        className={`form-control ${errors.username ? 'is-invalid' : ''}`}
                        required
                    />
                    {errors.username && <div className="invalid-feedback">{errors.username}</div>}
                </div>

                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                        required
                    />
                    {errors.email && <div className="invalid-feedback">{errors.email}</div>}
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                        required
                    />
                    {errors.password && <div className="invalid-feedback">{errors.password}</div>}
                </div>

                <div className="form-group">
                    <label htmlFor="password2">Confirm Password</label>
                    <input
                        type="password"
                        id="password2"
                        name="password2"
                        value={formData.password2}
                        onChange={handleChange}
                        className={`form-control ${errors.password2 ? 'is-invalid' : ''}`}
                        required
                    />
                    {errors.password2 && <div className="invalid-feedback">{errors.password2}</div>}
                </div>

                <button type="submit" className="btn btn-primary">Sign Up</button>
            </form>
        </div>
    );
};

export default Signup;