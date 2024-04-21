import os
import shutil
from src.agent import Agent
from src.config.command import Navigate, Sleep, SaveHtml, move_file, CollectNodes
from src.config.operations import BrowserOperations

if __name__ == '__main__':

    '''
    Collect Html for the webpage
    
    click on all elements of the webpage
    
    wait one second
    
    check if the html has changed
    
    check if the url has changed if so disregard
    
    otherwise save and collect
    
    once all html pages have been collected perform image analysis
    '''

    navigate_command = Navigate("https://www.dialpad.com/enterprise/")
    sleep_command = Sleep(2)
    save_html = SaveHtml("s1")
    collect_nodes = CollectNodes("body", "s1", True)

    operation = BrowserOperations()
    operation.append(navigate_command)
    operation.append(sleep_command)
    operation.append(save_html)
    operation.append(collect_nodes)

    a = Agent([operation])
    a.run(verbose=True)

    shutil.rmtree("localResources")
    os.makedirs("localResources/o1")
    move_file(save_html, "localResources/o1")
    move_file(collect_nodes, "localResources/o1")

    print(collect_nodes.load_json())

    for node in collect_nodes.load_json():
        if node.type == "Element":
            print(node.tag)


