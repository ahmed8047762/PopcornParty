// src/Navbar.js
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Navbar = () => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            const accessToken = localStorage.getItem('access_token');

            if (!refreshToken || !accessToken) {
                console.log('No tokens found');
                localStorage.clear();
                navigate('/login');
                return;
            }

            // Configure axios with the access token
            const config = {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                }
            };

            // Make the logout request with the configured headers
            const response = await axios.post(
                'http://127.0.0.1:8000/api/accounts/logout/',
                { refresh: refreshToken },
                config
            );

            if (response.status === 200) {
                // Clear tokens from local storage
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                alert('Logged out successfully!');
                navigate('/login');
            }
        } catch (error) {
            console.error('Error logging out:', error);
            if (error.response) {
                console.error('Error response:', error.response.data);
                if (error.response.status === 401) {
                    // If unauthorized, clear tokens and redirect to login
                    localStorage.clear();
                    navigate('/login');
                } else {
                    alert(`Failed to log out: ${error.response.data.detail || 'Unknown error'}`);
                }
            } else {
                alert('Failed to log out: Network error');
            }
        }
    };

    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-light">
            <Link className="navbar-brand" to="/">Movie2gether</Link>
            <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbarNav">
                <ul className="navbar-nav mr-auto">
                    <li className="nav-item">
                        <Link className="nav-link" to="/">Home</Link>
                    </li>
                    <li className="nav-item">
                        <Link className="nav-link" to="/login">Login</Link>
                    </li>
                    <li className="nav-item">
                        <Link className="nav-link" to="/signup">Sign Up</Link>
                    </li>
                    <li className="nav-item">
                        <button className="nav-link btn" onClick={handleLogout}>Logout</button>
                    </li>
                </ul>
            </div>
        </nav>
    );
};

export default Navbar;