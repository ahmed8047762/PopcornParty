// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import Signup from './Signup';
import Login from './Login';
import MovieSearch from './MovieSearch';
import CreateEvent from './CreateEvent';
import Invite from './Invite';
import MyInvitations from './MyInvitations';
import Navbar from './Navbar';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

const App = () => {
    return (
        <Router>
            <Navbar />
            <div className="container">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/signup" element={<Signup />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/movies" element={<MovieSearch />} />
                    <Route path="/create-event" element={<CreateEvent />} />
                    <Route path="/invite/:eventId" element={<Invite />} />
                    <Route path="/my-invitations" element={<MyInvitations />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;