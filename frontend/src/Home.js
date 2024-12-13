// src/Home.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Home = () => {
    const [events, setEvents] = useState([]);

    useEffect(() => {
        // Fetch events from the Django API
        axios.get('http://127.0.0.1:8000/api/events/')
            .then(response => {
                setEvents(response.data);
            })
            .catch(error => {
                console.error('Error fetching events:', error);
            });
    }, []);

    const handleJoinRequest = (eventId) => {
        // Logic for handling join request
        console.log('Request to join event:', eventId);
        // Redirect to login if not authenticated (you can implement this logic)
    };

    return (
        <div className="container">
            <h1 className="mt-4">Available Events</h1>
            <div className="list-group">
                {events.map(event => (
                    <div key={event.id} className="list-group-item">
                        <h5>{event.title}</h5>
                        <p>{event.description}</p>
                        <button 
                            className="btn btn-primary" 
                            onClick={() => handleJoinRequest(event.id)}>
                            Request to Join
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Home;