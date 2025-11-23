import torch
import torch.nn.functional as F

class GradCAM:
    def __init__(self, model, target_layer_name: str):
        self.model = model
        self.target_layer_name = target_layer_name
        self.gradients = None
        self.activations = None

        # Register hooks
        target_layer = dict(model.named_modules())[target_layer_name]
        target_layer.register_forward_hook(self._forward_hook)
        target_layer.register_backward_hook(self._backward_hook)

    def _forward_hook(self, module, inp, out):
        self.activations = out

    def _backward_hook(self, module, grad_in, grad_out):
        self.gradients = grad_out[0]

    def generate(self, input_tensor, class_idx=None):
        """
        input_tensor: 1 x C x H x W
        """
        self.model.zero_grad()
        logits = self.model(input_tensor)
        if class_idx is None:
            class_idx = logits.argmax(dim=1).item()

        score = logits[:, class_idx]
        score.backward(retain_graph=True)

        grads = self.gradients   # [B, C, H, W]
        activs = self.activations

        weights = grads.mean(dim=(2, 3), keepdim=True)
        cam = (weights * activs).sum(dim=1, keepdim=True)
        cam = F.relu(cam)

        cam = cam.squeeze().detach().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam
