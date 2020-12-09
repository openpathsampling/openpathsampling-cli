def tag_final_result(result, storage, tag='final_conditions'):
    if storage:
        storage.save(result)
        storage.tags[tag] = result
