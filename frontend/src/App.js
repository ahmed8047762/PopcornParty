// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'; // Use Routes instead of Switch
import Home from './Home';
import Signup from './Signup';
import Login from './Login';
import Navbar from './Navbar'; // Import the Navbar component
import 'bootstrap/dist/css/bootstrap.min.css';

const App = () => {
    return (
        <Router>
            <Navbar /> {/* Add the Navbar here */}
            <div className="container">
                <Routes> {/* Use Routes instead of Switch */}
                    <Route path="/" element={<Home />} /> {/* Use element prop for rendering */}
                    <Route path="/signup" element={<Signup />} />
                    <Route path="/login" element={<Login />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;