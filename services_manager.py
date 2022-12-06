from utils.environment import env

if __name__ == "__main__":
    # Assumes that env var is being used. Will default to non-cuda if no env exists
    if env.service_name in ['integration', 'prediction']:
        from services_manager_cuda import handle
    else:
        from services_manager_cudaless import handle
    handle()