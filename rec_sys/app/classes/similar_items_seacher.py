from annoy import AnnoyIndex


class SimilarItemsSeacher:
    def __init__(
        self, 
        annoy_index: AnnoyIndex,
        annoy_index_to_item_id: dict,
        item_id_to_annoy_index: dict,
    ) -> None:
        """Класс для поиска похожих товаров

        Args:
            annoy_index (AnnoyIndex): объект с проиндексированными товарами
            annoy_index_to_item_id (dict): соответствие {индекс annoy} -> {id товара}
            item_id_to_annoy_index (dict): соответствие {id товара} -> {индекс annoy}
        """
        self.annoy_index = annoy_index
        
        # При загрузке из json файлов ключи в словаре соответствий будут строками
        # Переведем их в тип int, что соответствует типу ключей
        self.annoy_index_to_item_id = {
            int(ann_ind): item_id for ann_ind, item_id in annoy_index_to_item_id.items()
        }
        self.item_id_to_annoy_index = {
            int(item_id): ann_ind for item_id, ann_ind in item_id_to_annoy_index.items()
        }
        
    
    def get(self, item_id: int, items_count: int = 3) -> list:
        """Возвращает похожие товары

        Args:
            item_id (int): id товара, для которого нужно найти похожие
            items_count (int, optional): Сколько нужно вернуть похожих товаров. 
                                         По умолчанию 3.

        Returns:
            list: похожие товары
        """
        if item_id not in self.item_id_to_annoy_index:
            return []
        
        index_in_annoy = self.item_id_to_annoy_index[item_id]
        
        similar_indexes = self.annoy_index.get_nns_by_item(
            index_in_annoy, items_count + 1
        )[1:] # исключаем сам товар
        
        return [self.annoy_index_to_item_id[i] for i in similar_indexes]
