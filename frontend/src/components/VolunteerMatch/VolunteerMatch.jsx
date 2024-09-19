import { useState } from "react";
import styles from "./VolunteerMatch.module.css";

const VolunteerMatch = () =>{
  const [selectedVolunteer, setSelectedVolunteer] = useState('');
  const [matchedEvents, setMatchedEvents] = useState([]);

  // Dummy data for volunteers
  const volunteers = [
    { id: 1, name: 'John Doe' },
    { id: 2, name: 'Jane Smith' },
    { id: 3, name: 'Alice Johnson' }
  ];

  // Dummy function to simulate matching events
  const matchVolunteer = (volunteerId) => {
    // Dummy data for events based on the selected volunteer
    const dummyEvents = {
      1: [{ id: 1, event_name: 'First Aid Workshop', location: 'New York' }],
      2: [{ id: 2, event_name: 'Fundraising Gala', location: 'Los Angeles' }],
      3: [{ id: 3, event_name: 'Community Clean-up', location: 'San Francisco' }],
    };
    
    // Set the matched events for the selected volunteer
    setMatchedEvents(dummyEvents[volunteerId] || []);
  };

  const handleMatch = (e) => {
    e.preventDefault();
    
    // Ensure a volunteer is selected
    if (!selectedVolunteer) {
      alert('Please select a volunteer');
      return;
    }

    // Simulate the matching logic
    matchVolunteer(selectedVolunteer);
  };

  return (
    <div className={styles.App}>
      <h1>Volunteer Matching Form</h1>

      <form onSubmit={handleMatch} className={styles.form}>
        <label htmlFor="volunteer" className={styles.label}>Select Volunteer:</label>
        <select
          name="volunteer_id"
          id="volunteer_id"
          value={selectedVolunteer}
          onChange={(e) => setSelectedVolunteer(e.target.value)}
          className={styles.select}
        >
          <option value="">--Select a Volunteer--</option>
          {volunteers.map((volunteer) => (
            <option key={volunteer.id} value={volunteer.id}>
              {volunteer.name}
            </option>
          ))}
        </select>

        <button type="submit" className={styles.button}>Match Volunteer</button>
      </form>

      <div className={styles.matchedEvents}>
        <h2>Matched Events</h2>

        {matchedEvents.length > 0 ? (
          <ul className={styles.eventsList}>
            {matchedEvents.map((event) => (
              <li key={event.id} className={styles.eventItem}>
                {event.event_name} (Location: {event.location})
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.noEvents}>No events matched for the selected volunteer.</p>
        )}
      </div>
    </div>
  );
}

export default VolunteerMatch;