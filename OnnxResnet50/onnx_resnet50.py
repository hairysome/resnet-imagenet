
import numpy as np

import bentoml
from bentoml.artifact import OnnxModelArtifact, PickleArtifact
from bentoml.handlers import ImageHandler


@bentoml.env(auto_pip_dependencies=True)
@bentoml.artifacts([OnnxModelArtifact('model'), PickleArtifact('labels')])
class OnnxResnet50(bentoml.BentoService):
    def preprocess(self, input_data):
        # convert the input data into the float32 input
        img_data = input_data.transpose(2, 0, 1).astype('float32')

        #normalize
        mean_vec = np.array([0.485, 0.456, 0.406])
        stddev_vec = np.array([0.229, 0.224, 0.225])
        norm_img_data = np.zeros(img_data.shape).astype('float32')
        for i in range(img_data.shape[0]):
            norm_img_data[i,:,:] = (img_data[i,:,:]/255 - mean_vec[i]) / stddev_vec[i]
        
        #add batch channel
        norm_img_data = norm_img_data.reshape(1, 3, 224, 224).astype('float32')
        return norm_img_data
    
    def softmax(self, x):
        x = x.reshape(-1)
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)
    
    def post_process(self, raw_result):
        return self.softmax(np.array(raw_result)).tolist()

 
    @bentoml.api(ImageHandler)
    def predict(self, image_data):
        input_data = self.preprocess(image_data)
        input_name = self.artifacts.model.get_inputs()[0].name
        raw_result = self.artifacts.model.run([], {input_name: input_data})
        result = self.post_process(raw_result)
        idx = np.argmax(result)
        sort_idx = np.flip(np.squeeze(np.argsort(result)))
        
        # return top 5 labels
        return self.artifacts.labels[sort_idx[:5]]
        
