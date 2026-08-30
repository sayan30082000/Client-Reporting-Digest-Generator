import json

def process_hackathon_data(input_file, output_file):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Your team ID
    team_id = "LSH26-T056"
    output_cases = []

    for case in data.get('cases', []):
        case_id = case['case_id']
        current_month = case['current_month']
        previous_month = case['previous_month']
        alerts = case.get('alerts', [])

        out_case = {
            "team_id": team_id,
            "case_id": case_id,
            "current_month": current_month,
            "previous_month": previous_month,
            "alerts": alerts,
            "clients": []
        }

        for client in case.get('clients', []):
            client_id = client['id']
            client_name = client['name']

            out_measures = []
            breaches = []
            valid_percents = []
            rose_count = 0
            fell_count = 0

            # Calculate for each Measure
            for m in client.get('measures', []):
                measure_name = m['measure']
                last_val = float(m['last'])
                current_val = float(m['current'])
                
                # Delta
                delta = current_val - last_val
                
                # No Baseline check
                no_baseline = (last_val == 0.0)

                # Percent
                if no_baseline:
                    percent = None
                else:
                    percent = (delta / last_val) * 100

                # Direction
                direction = "flat"
                if delta > 0:
                    direction = "up"
                    rose_count += 1
                elif delta < 0:
                    direction = "down"
                    fell_count += 1

                # Format the output for the measure
                out_m = {
                    "measure": measure_name,
                    "last": f"{last_val:.2f}",
                    "current": f"{current_val:.2f}",
                    "delta": f"{delta:.2f}",
                    "percent": f"{percent:.2f}" if percent is not None else None,
                    "direction": direction,
                    "no_baseline": no_baseline
                }
                out_measures.append(out_m)

                # Save percentage to calculate Movers
                if percent is not None:
                    valid_percents.append((measure_name, abs(percent)))

                # Check Alerts (Breaches)
                for alert in alerts:
                    if alert['measure'] == measure_name:
                        level = float(alert['level'])
                        is_breach = False
                        
                        if alert['direction'] == 'above' and current_val > level:
                            is_breach = True
                        elif alert['direction'] == 'below' and current_val < level:
                            is_breach = True

                        if is_breach:
                            breaches.append({
                                "measure": measure_name,
                                "direction": alert['direction'],
                                "level": alert['level'],
                                "value": f"{current_val:.2f}"
                            })

            # Movers: Top 2 measures with the largest absolute percentage change
            valid_percents.sort(key=lambda x: x[1], reverse=True)
            movers = [x[0] for x in valid_percents[:2]]

            # Generate basic summary
            summary = f"{client_name} in {current_month}, against {previous_month}. {rose_count} of {len(out_measures)} measures rose, {fell_count} fell."

            # Construct complete client data
            out_client = {
                "id": client_id,
                "name": client_name,
                "summary": summary,
                "summary_edited": False,
                "movers": movers,
                "measures": out_measures,
                "breaches": breaches
            }
            out_case['clients'].append(out_client)

        output_cases.append(out_case)

    # Generate final output
    final_output = {
        "team_id": team_id,
        "cases": output_cases
    }

    # Save to output.json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2)

if __name__ == "__main__":
    process_hackathon_data('P06.json', 'output.json')
    print("Success! All calculations are done. Check the 'output.json' file.")