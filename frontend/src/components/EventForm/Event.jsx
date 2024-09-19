import React from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import styles from "./Event.module.css";
import {useState} from 'react';
import Select from 'react-select';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";



// Validation schema using Yup
const EventSchema = Yup.object().shape({
  eventName: Yup.string().min(100, "Event name must be at least 100 characters").required("Required"),
  eventDescription: Yup.string().required("You must enter a description"),
  location: Yup.string().required("You must enter a location"),
  requiredSkills: Yup.array().min(1, 'At least one skill is required').required('Required'),
  urgency: Yup.string().required('Urgency is required'),
  eventDate: Yup.date().required('Event date is required'),
});

const options = [
  { value: 'Carry over 50 lbs', label: 'Carry over 50 lbs' },
  { value: 'Run over 20 miles', label: 'Run over 50 miles' },
]



const Event = () => {
  const [startDate, setStartDate] = useState(new Date());

  return (
    <div className={styles.eventContainer}>
      <h2>Event Management Form</h2>
      <Formik
        initialValues={{
          eventName: "",
          eventDescription: "",
          location: "",
          requiredSkills: [],
          urgency: '',
          eventDate: null,
        }}
        validationSchema={EventSchema}
        onSubmit={(values) => {
          console.log("Registration successful!", values);
          alert("Registration successful!");
        }}
      >
        {({setFieldValue, isSubmitting }) => (
          <Form>
            <div>
              <label htmlFor="eventName">Event Name</label>
              <Field type="text" name="eventName" />
              <ErrorMessage name="eventName" component="div" className={styles.error} />
            </div>
            <div>
              <label htmlFor="eventDescription">Event Description</label>
              <Field as="textarea" name="eventDescription" />
              <ErrorMessage name="eventDescription" component="div" className={styles.error} />
            </div>
            <div>
              <label htmlFor="location">Location</label>
              <Field as="textarea" name="location" />
              <ErrorMessage name="location" component="div" className={styles.error} />
            </div>

            {/* Multi-select for Required Skills */}
            {/* <div>
              <label htmlFor="requiredSkills">Required Skills</label>
              <Field name="requiredSkills">
                {({ field, form }) => (
                  <select
                    {...field}
                    name="requiredSkills"
                    multiple={true}
                    value={field.value || []} // Ensure sync
                    onChange={(event) => {
                      const selectedOptions = Array.from(event.target.selectedOptions, (option) => option.value);
                      form.setFieldValue(field.name, selectedOptions);
                    }}
                  >
                    <option value="JavaScript">JavaScript</option>
                    <option value="Python">Python</option>
                    <option value="React">React</option>
                    <option value="Node.js">Node.js</option>
                  </select>
                )}
              </Field>
              <ErrorMessage name="requiredSkills" component="div" className={styles.error} />
            </div> */}

            {/* Dropdown for Urgency */}
            <div>
              <label htmlFor="urgency">Urgency</label>
              <Field as="select" name="urgency">
                <option value="">Select urgency</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </Field>
              <ErrorMessage name="urgency" component="div" className={styles.error} />
            </div>
          </Form>
        )}
      </Formik>
      
      <div>
       <div>Required Skills</div>
       <Select options={options} isMulti/>
      </div>

      <div>
       <div>Select Date</div>
       <DatePicker selected={startDate} onChange={(date) => setStartDate(date)} />
      </div>



     <button type="submit">Submit</button>
    </div>
  );
};

export default Event;
