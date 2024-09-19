import React, { useState, useEffect } from "react";
import styles from "./volunteerHistory.module.css";

const data = [
  {
    eventName: "These are all dummy info",
    description: "These are all dummy info",
    location: "These are all dummy info",
    requiredSkills: "Dummy info",
    urgency: "Dummy info",
    date: "These are all dummy info",
    participationStatus: "Dummy info"
  },
  {
    eventName: "Houston Marathon",
    description: "gave water to runners",
    location: "Houston, TX",
    requiredSkills: "Water handing skills max lvl",
    urgency: "Urgent",
    date: "January 2023",
    participationStatus: "Not Participating"
  },
  {
    eventName: "These are all dummy info",
    description: "These are all dummy info",
    location: "These are all dummy info",
    requiredSkills: "Dummy info",
    urgency: "Dummy info",
    date: "These are all dummy info",
    participationStatus: "Dummy info"
  }
];

const VolunteerHistory = () => {
  const [info, setInfo] = useState([]);

  useEffect(() => {
    setInfo(data);
  }, []);

  return (
    <div className={styles.page}>
      <div className={styles.volunteerContainer}>
        <h2 className={styles.title}>Volunteer History</h2>
        <div className={styles.historyContainer}>
          {info.length === 0 ? (
            <h3>No volunteer history</h3>
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
      </div>
    </div>
  );
};

export default VolunteerHistory;
