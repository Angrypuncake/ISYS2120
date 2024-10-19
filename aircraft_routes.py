from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import database
import re
aircraft_bp = Blueprint('aircraft', __name__)


@aircraft_bp.route('/aircrafts')
def list_aircrafts():
    print(session)

    aircrafts = database.list_aircraft()
    
    # Handle empty aircraft list
    if not aircrafts:
        aircrafts = []
        flash('No aircrafts found', 'danger')
        
    # Return the template with session and page variables
    return render_template('list_aircrafts.html', aircrafts=aircrafts, session=session, page={'title': 'Aircraft List'})

@aircraft_bp.route('/aircraft/<int:aircraft_id>')
def view_aircraft(aircraft_id):
    aircraft = database.get_aircraft_by_id(aircraft_id)
    
    # Handle case where aircraft is not found
    if not aircraft:
        flash(f'Aircraft with ID {aircraft_id} not found', 'danger')
        return redirect(url_for('aircraft.list_aircrafts'))
    
    return render_template('view_aircraft.html', aircraft=aircraft, session=session, page={'title': 'View Aircraft'})

@aircraft_bp.route('/add_aircraft', methods=['GET', 'POST'])


def add_aircraft():
    if request.method == 'POST':
        aircraft_id = request.form['AircraftID']
        icao_code = request.form['ICAOCode']
        registration = request.form['AircraftRegistration']
        name = request.form['Name']
        manufacturer = request.form['Manufacturer']
        model = request.form['Model']

        # Input Validation
        errors = []

        # Check if aircraft_id is a valid integer and less than 10^6
        try:
            aircraft_id = int(aircraft_id)
            if aircraft_id >= 10**6:
                errors.append("Aircraft ID should be less than 1,000,000.")
        except ValueError:
            errors.append("Aircraft ID must be a valid integer.")

        # Validate ICAO Code format (starts with a letter and ends with 3 digits)
        if not re.match(r'^[A-Za-z]\d{3}$', icao_code):
            errors.append("ICAO Code must start with a letter and end with 3 digits (e.g., 'D123').")

        # Validate Registration format (e.g., XX-YYY or XX-Y12)
        if not re.match(r'^[A-Za-z]{2}-[A-Za-z0-9]{3}$', registration):
            errors.append("Registration must follow the format 'XX-YYY' or 'XX-Y12'.")

        # Check if name exceeds 50 characters
        if len(name) > 100:
            errors.append("Name cannot exceed 100 characters.")

        if len(manufacturer) > 100:
            errors.append("Name cannot exceed 100 characters.")

        if len(model) > 100:
            errors.append("Name cannot exceed 100 characters.")

        # Check if the aircraft ID is already in the database
        existing_aircraft = database.get_aircraft_by_id(aircraft_id)
        if existing_aircraft:
            errors.append(f"Aircraft ID {aircraft_id} already exists in the database.")

        # If there are validation errors, flash them and return to form
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('add_aircraft.html', session=session, page={'title': 'Add Aircraft'})

        try:
            # Add aircraft to the database
            database.add_aircraft(aircraft_id, icao_code, registration, name, manufacturer, model)
            flash('Aircraft added successfully!', 'success')
            return redirect(url_for('aircraft.list_aircrafts'))
        except Exception as e:
            flash(f'Error adding aircraft: {str(e)}', 'error')
            return render_template('add_aircraft.html', session=session, page={'title': 'Add Aircraft'})

    # If request method is GET, render the form
    return render_template('add_aircraft.html', session=session, page={'title': 'Add Aircraft'})


@aircraft_bp.route('/update_aircraft/<int:aircraft_id>', methods=['GET', 'POST'])
def update_aircraft(aircraft_id):
    aircraft = database.get_aircraft_by_id(aircraft_id)
    
    # Handle case where aircraft is not found
    if not aircraft:
        flash(f'Aircraft with ID {aircraft_id} not found', 'error')
        return redirect(url_for('aircraft.list_aircrafts'))

    if request.method == 'POST':
        # Extract form data
        icao_code = request.form.get('ICAOCode', '').strip()
        registration = request.form.get('AircraftRegistration', '').strip()
        name = request.form.get('Name', '').strip()
        manufacturer = request.form.get('Manufacturer', '').strip()
        model = request.form.get('Model', '').strip()

        # Input Validation
        errors = []

        # Validate ICAO Code format (starts with a letter and ends with 3 digits)
        if not re.match(r'^[A-Za-z]\d{3}$', icao_code):
            errors.append("ICAO Code must start with a letter and end with 3 digits (e.g., 'D123').")

        # Validate Registration format (e.g., XX-YYY or XX-Y12)
        if not re.match(r'^[A-Za-z]{2}-[A-Za-z0-9]{3}$', registration):
            errors.append("Registration must follow the format 'XX-YYY' or 'XX-Y12'.")

        # Check if name exceeds 100 characters
        if len(name) > 100:
            errors.append("Name cannot exceed 100 characters.")
        
        # Check if manufacturer exceeds 100 characters
        if len(manufacturer) > 100:
            errors.append("Manufacturer cannot exceed 100 characters.")
        
        # Check if model exceeds 100 characters
        if len(model) > 100:
            errors.append("Model cannot exceed 100 characters.")

        # If there are validation errors, flash them and return to form
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('update_aircraft.html', aircraft=aircraft, session=session, page={'title': 'Update Aircraft'})

        # Perform the update if all validations pass
        try:
            database.update_aircraft(aircraft_id, icao_code, registration, name, manufacturer, model)
            flash('Aircraft updated successfully!', 'success')
            return redirect(url_for('aircraft.view_aircraft', aircraft_id=aircraft_id))
        except Exception as e:
            flash(f'Error updating aircraft: {str(e)}', 'error')
            return render_template('update_aircraft.html', aircraft=aircraft, session=session, page={'title': 'Update Aircraft'})

    return render_template('update_aircraft.html', aircraft=aircraft, session=session, page={'title': 'Update Aircraft'})

@aircraft_bp.route('/delete_aircraft/<int:aircraft_id>', methods=['POST'])
def delete_aircraft(aircraft_id):
    # Delete aircraft from the database
    database.delete_aircraft(aircraft_id)
    flash(f'Aircraft with ID {aircraft_id} has been deleted.')
    return redirect(url_for('aircraft.list_aircrafts'))

@aircraft_bp.route('/aircraft_summary')
def aircraft_summary():
    summary = database.aircraft_summary()
    
    # Handle case where summary data is empty
    if not summary:
        flash('No aircraft summary available.')
    
    return render_template('aircraft_summary.html', summary=summary, session=session, page={'title': 'Aircraft Summary'})


@aircraft_bp.route('/search_aircraft_by_id', methods=['GET', 'POST'])
def search_aircraft_by_id():
    if request.method == 'POST':
        # Get the aircraft ID from the form
        aircraft_id = request.form.get('aircraft_id')

        if aircraft_id:
            # Query the database for the aircraft by ID
            aircraft = database.get_aircraft_by_id(int(aircraft_id))
            
            # Handle case where aircraft is not found
            if not aircraft:
                flash(f'Aircraft with ID {aircraft_id} not found.', 'warning')
                return redirect(url_for('aircraft.search_aircraft_by_id'))

            # If aircraft is found, render the details page
            return render_template('view_aircraft.html', aircraft=aircraft, page={'title': 'Aircraft Details'})

    # Render the search page when accessed via GET or after POST
    return render_template('search_aircraft_by_id.html', page={'title': 'Search Aircraft by ID'})
