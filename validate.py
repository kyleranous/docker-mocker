"""
Validation functions to validate teh data used to create MockDocker instances
"""
import json

def validate_swarm_data(swarm_dict):
    """
    Loops through the swarm definitions and validates that data is present and correct
    """
    response = {}
    swarm_ids = {}

    for idx, swarm in enumerate(swarm_dict):
        error_list = []
        swarm_key = swarm.get('id')
        # Check for Swarm id
        if swarm.get('id') is None:
            # If No id, create temporary id and add id error to error list
            swarm_key = f'swarm_{idx}_no_id'
            error_list.append({'id_error': 'Swarm ID is required'})
        else:
            # If id, add to swarm_ids dict to verify uniqueness
            if swarm['id'] in swarm_ids.keys():
                error_list.append({'id_error': f'Swarm ID must be unique, duplicate found at index: {swarm_ids[swarm["id"]]} and {idx}'})
            else:
                # If id is not in swarm_ids, add to swarm_ids
                swarm_ids[swarm_key] = idx 

        # Check swarm state is a valid option
        if swarm.get('state') is None:
            # If state not in swarm, add state error to error list
            error_list.append({'state_error': 'Swarm state is required'})
        elif swarm['state'] not in ['success', 'locked', 'fail']:
            error_list.append({'state_error': 'Swarm state must be success or locked'})
        # If swarm state is locked, UnlockKey must be present
        if swarm.get('state') == 'locked' and swarm.get('UnlockKey') is None:
            error_list.append({'UnlockKey_error': 'Swarm status is locked, UnlockKey is required'})

        # check for attributes
        if swarm.get('attrs') is None:
            error_list.append({'attrs_error': 'Swarm attrs is required'})
        else:
            # Check for required attrs
            attrs = swarm['attrs']
            if attrs.get('ID') is None:
                error_list.append({'attrs_ID_error': 'Swarm attrs ID is required'})
            # Check for Spec dictionary
            if attrs.get('Spec') is None:
                error_list.append({'attrs_Spec_error': 'Swarm attrs Spec is required'})
            else:
                spec = attrs['Spec']
                # Check for required Spec attrs
                if spec.get('Name') is None:
                    error_list.append({'attrs_Spec_Name_error': 'Swarm attrs Spec Name is required'})
            
            # Check for Work and Manager Join Tokens
            if attrs.get('JoinTokens') is None:
                error_list.append({'attrs_JoinTokens_error': 'Swarm attrs JoinTokens is required'})
            else:
                tokens = attrs['JoinTokens']
                if tokens.get('Worker') is None:
                    error_list.append({'attrs_JoinTokens_Worker_error': 'Swarm attrs JoinTokens Worker is required'})
                if tokens.get('Manager') is None:
                    error_list.append({'attrs_JoinTokens_Manager_error': 'Swarm attrs JoinTokens Manager is required'})
                

        # Add error list to response dict
        if len(error_list) > 0:
            response[swarm_key] = error_list
    
    return response

def validate_node_data(node_dict):
    return {}

def __main__():
    """
    Takes in a file path as an argument and parses the file to check if it is a 
    valid client_dict definition json
    """
    import argparse
    import os
    parser = argparse.ArgumentParser(description='Validate client_dict definition json')
    parser.add_argument('file_path', help='File path to client_dict definition json')
    args = parser.parse_args()
    file_path = args.file_path
    script_dir = os.path.dirname(__file__)

    abs_file_path = os.path.join(script_dir, file_path)
    with open(abs_file_path, 'r') as client_dict_file:
        client_dict = json.load(client_dict_file)
    
    # Validate Swarm Entries
    if client_dict.get('swarms') is not None:
        response = validate_swarm_data(client_dict['swarms'])
        if len(response) > 0:
            print('*'*10, 'Swarm Validation Failed', '*'*10)
            print(f"{len(client_dict['swarms'])} Checked, {len(response)} Failed - {(len(response) / len(client_dict['swarms']))*100}%\n")
            for key, swarm in response.items():
                print(f"{key}:")
                for error in swarm:
                    for ekey, msg in error.items():
                        print(f"\t{ekey}: {msg}")
                print('\n')
        else:
            print('*'*10, 'Swarm Validation Successful', '*'*10)
            print(f"{len(client_dict['swarms'])} Checked\n")
    else:
        print("No Swarms to Validate\n")
    
    # Validate Node Entries
    if client_dict.get('nodes') is not None:
        response = validate_node_data(client_dict['nodes'])
        if len(response) > 0:
            print('*'*10, 'Node Validation Failed', '*'*10)
            print(f"{len(client_dict['nodes'])} Checked, {len(response)} Failed - {(len(response) / len(client_dict['nodes']))*100}%")
            for key, swarm in response.items():
                print(f"{key}:")
                for error in swarm:
                    for ekey, msg in error.items():
                        print(f"\t{ekey}: {msg}")
        else:
            print('*'*10, 'Node Validation Successful', '*'*10)
            print(f"{len(client_dict['nodes'])} Checked")
    else:
        print("No Nodes to Validate")
        

if __name__ == '__main__':
    __main__()
