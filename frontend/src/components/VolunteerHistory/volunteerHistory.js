import React, { useState, useEffect } from "react";
import styles from "./volunteerHistory.module.css";

const data = [
  {
    date: "January 2024",
    description: "Feed 100 homeless people.",
    role: "Chogath"
  },
  {
    date: "June 2028",
    description: "Save 10 babies from a burning building.",
    role: "Nami"
  },
  {
    date: "July 2023",
    description: "Saved 80 animals from drowning.",
    role: "Nidalee"
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
                <p className={styles.role}><strong>Role:</strong> {entry.role}</p>
                <p className={styles.date}><strong>Date:</strong> {entry.date}</p>
                <p className={styles.description}><strong>Description:</strong> {entry.description}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default VolunteerHistory;
