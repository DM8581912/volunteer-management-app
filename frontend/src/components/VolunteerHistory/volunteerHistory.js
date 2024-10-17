import React, { useState, useEffect } from "react";
import styles from "./volunteerHistory.module.css";

const VolunteerHistory = ({ username }) => {
  const [info, setInfo] = useState([]);
  const [error, setError] = useState(null);


  useEffect(() => {
    const fetchVolunteerHistory = async () => {
      try {
        const response = await fetch(`http://localhost:5000/volunteer/${username}/history`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setInfo(data.history);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchVolunteerHistory();
  }, [username]);

  const addEvent = async (newEvent) => {
    try {
      const response = await fetch(`http://localhost:5000/volunteer/${username}/history`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newEvent),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setInfo(data.history);
    } catch (err) {
      console.error("Error adding event:", err);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.volunteerContainer}>
        <h2 className={styles.title}>Volunteer History</h2>
        {error ? (
          <p className={styles.error}>Error: {error}</p>
        ) : (
          <div className={styles.historyContainer}>
            {info.length === 0 ? (
              <h3>No volunteer history available</h3>
            ) : (
              info.map((entry, index) => (
                <div key={index} className={styles.event}>
                  <p className={styles.information}><strong>Event:</strong> {entry.eventName}</p>
                  <p className={styles.information}><strong>Date:</strong> {entry.date}</p>
                  <p className={styles.information}><strong>Location:</strong> {entry.location}</p>
                  <p className={styles.information}><strong>Required Skills:</strong> {entry.requiredSkills}</p>
                  <p className={styles.information}><strong>Urgency:</strong> {entry.urgency}</p>
                  <p className={styles.information}><strong>Description:</strong> {entry.description}</p>
                  <p className={styles.information}><strong>Participation Status:</strong> {entry.participationStatus}</p>
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