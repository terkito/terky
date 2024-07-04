
git clone https://github.com/facefusion/facefusion.git
git clone https://github.com/facefusion/facefusion-docker.git


content_analyser.py para erliminar y editar porno

def analyse_frame(vision_frame : VisionFrame) -> bool:
    # content_analyser = get_content_analyser()
    # vision_frame = prepare_frame(vision_frame)
    # with conditional_thread_semaphore(facefusion.globals.execution_providers):
    #     probability = content_analyser.run(None, {
    #         content_analyser.get_inputs()[0].name: vision_frame
    #     })[0][0][1]
    # return probability > PROBABILITY_LIMIT
    return False

para ejecutarlo
docker-compose -f docker-compose.cpu.yml up --build


limpiar docker e iniciar nuevamente

docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

docker rmi $(docker images -a -q)

docker volume prune

docker network prune


Link de Donate segundo boton
terky/facefusion/uis/components/about.py

Link primer boton
terky/facefusion/metadata.py
