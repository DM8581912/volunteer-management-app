import { useState, useEffect } from "react";
import styles from "./VolunteerMatch.module.css";
import { toast } from "react-toastify";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

const VolunteerMatch = () => {
  const [selectedVolunteer, setSelectedVolunteer] = useState("");
  const [matchedEvents, setMatchedEvents] = useState([]);
  const [volunteers, setVolunteers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchVolunteers = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/eventform`);
        if (response.ok) {
          const data = await response.json();
          setVolunteers(data.events || []);
        }
      } catch (err) {
        toast.error("Failed to load data");
      }
    };
    fetchVolunteers();
  }, []);

  const handleMatch = async (e) => {
    e.preventDefault();

    if (!selectedVolunteer) {
      toast.error("Please select a volunteer");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/matches/volunteer/${selectedVolunteer}`
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "Failed to find matches");
      }

      const data = await response.json();
      setMatchedEvents(data.matches || []);

      if (!data.matches || data.matches.length === 0) {
        toast.info("No matching events found for this volunteer");
      }
    } catch (err) {
      toast.error(err.message);
      setMatchedEvents([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.App}>
      <h1>Volunteer Matching Form</h1>

      <form onSubmit={handleMatch} className={styles.form}>
        <label htmlFor="volunteer_id" className={styles.label}>
          Select Volunteer:
        </label>
        <input
          type="text"
          id="volunteer_id"
          value={selectedVolunteer}
          onChange={(e) => setSelectedVolunteer(e.target.value)}
          className={styles.select}
          placeholder="Enter volunteer username"
        />

        <button type="submit" className={styles.button} disabled={isLoading}>
          {isLoading ? "Matching..." : "Match Volunteer"}
        </button>
      </form>

      <div className={styles.matchedEvents}>
        <h2>Matched Events</h2>

        {matchedEvents.length > 0 ? (
          <ul className={styles.eventsList}>
            {matchedEvents.map((match, index) => (
              <li key={match.event?.id || index} className={styles.eventItem}>
                {match.event?.eventName} (Location: {match.event?.location}) -
                Match Score: {Math.round(match.matchScore)}%
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.noEvents}>
            No events matched for the selected volunteer.
          </p>
        )}
      </div>
    </div>
  );
};

export default VolunteerMatch;
