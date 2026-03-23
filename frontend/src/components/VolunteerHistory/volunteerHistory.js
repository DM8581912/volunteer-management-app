import React, { useState, useEffect } from "react";
import styles from "./volunteerHistory.module.css";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

const VolunteerHistory = ({ username }) => {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!username) {
      setError("No username provided");
      setIsLoading(false);
      return;
    }

    const fetchVolunteerHistory = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/volunteer/${username}/history`);
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || `Server error (${response.status})`);
        }
        const data = await response.json();
        setHistory(data.history || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchVolunteerHistory();
  }, [username]);

  const addEvent = async (newEvent) => {
    try {
      const response = await fetch(`${API_BASE_URL}/volunteer/${username}/history`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newEvent),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "Failed to add event");
      }

      const data = await response.json();
      setHistory((prev) => [...prev, data.history]);
    } catch (err) {
      setError(err.message);
    }
  };

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.volunteerContainer}>
          <h2 className={styles.title}>Volunteer History</h2>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.volunteerContainer}>
        <h2 className={styles.title}>Volunteer History</h2>
        {error ? (
          <p className={styles.error}>Error: {error}</p>
        ) : (
          <div className={styles.historyContainer}>
            {history.length === 0 ? (
              <h3>No volunteer history available</h3>
            ) : (
              history.map((entry, index) => (
                <div key={entry.id || index} className={styles.event}>
                  <p className={styles.information}><strong>Event:</strong> {entry.eventName || entry.eventname}</p>
                  <p className={styles.information}><strong>Date:</strong> {entry.eventDate || entry.eventdate || entry.date}</p>
                  <p className={styles.information}><strong>Location:</strong> {entry.location}</p>
                  <p className={styles.information}><strong>Required Skills:</strong> {Array.isArray(entry.requiredSkills || entry.requiredskills) ? (entry.requiredSkills || entry.requiredskills).join(", ") : entry.requiredSkills || entry.requiredskills}</p>
                  <p className={styles.information}><strong>Urgency:</strong> {entry.urgency}</p>
                  <p className={styles.information}><strong>Description:</strong> {entry.description}</p>
                  <p className={styles.information}><strong>Participation Status:</strong> {entry.participationStatus || entry.participationstatus}</p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VolunteerHistory;
