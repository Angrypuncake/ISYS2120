from flask import Blueprint, render_template, request, redirect, url_for, flash
import database

aircraft_bp = Blueprint('aircraft', __name__)

@aircraft_bp.route('/aircrafts')
def list_aircrafts():
    aircrafts = database.list_aircraft()
    if not aircrafts:
        flash('No aircrafts found')
    return render_template('list_aircrafts.html', aircrafts=aircrafts)

@aircraft_bp.route('/aircraft/<int:aircraft_id>')
def view_aircraft(aircraft_id):
    aircraft = database.get_aircraft_by_id(aircraft_id)
    if not aircraft:
        flash(f'Aircraft with ID {aircraft_id} not found')
        return redirect(url_for('aircraft.list_aircrafts'))
    return render_template('view_aircraft.html', aircraft=aircraft)

@aircraft_bp.route('/add_aircraft', methods=['GET', 'POST'])
def add_aircraft():
    if request.method == 'POST':
        aircraft_id = request.form['AircraftID']
        icao_code = request.form['ICAOCode']
        registration = request.form['AircraftRegistration']
        name = request.form['Name']
        manufacturer = request.form['Manufacturer']
        model = request.form['Model']
        database.add_aircraft(aircraft_id, icao_code, registration, name, manufacturer, model)
        return redirect(url_for('aircraft.list_aircrafts'))
    return render_template('add_aircraft.html')

@aircraft_bp.route('/update_aircraft/<int:aircraft_id>', methods=['GET', 'POST'])
def update_aircraft(aircraft_id):
    aircraft = database.get_aircraft_by_id(aircraft_id)
    if not aircraft:
        flash(f'Aircraft with ID {aircraft_id} not found')
        return redirect(url_for('aircraft.list_aircrafts'))

    if request.method == 'POST':
        icao_code = request.form['ICAOCode']
        registration = request.form['AircraftRegistration']
        name = request.form['Name']
        manufacturer = request.form['Manufacturer']
        model = request.form['Model']
        database.update_aircraft(aircraft_id, icao_code, registration, name, manufacturer, model)
        return redirect(url_for('aircraft.view_aircraft', aircraft_id=aircraft_id))

    return render_template('update_aircraft.html', aircraft=aircraft)

@aircraft_bp.route('/delete_aircraft/<int:aircraft_id>', methods=['POST'])
def delete_aircraft(aircraft_id):
    database.delete_aircraft(aircraft_id)
    return redirect(url_for('aircraft.list_aircrafts'))

@aircraft_bp.route('/aircraft_summary')
def aircraft_summary():
    summary = database.aircraft_summary()
    return render_template('aircraft_summary.html', summary=summary)
