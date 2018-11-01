import cv2, os, math
import numpy as np

class Slideshow():
    """
    Classe para criação de um slideshow a partir das fotos e configurações inseridas.

    :param dir_fotos: Path do diretório que mantém as fotos a serem utilizadas.
    :param dir_video: Path do diretório em que será armazenado o slideshow após criado.
    :param video_filename: Nome do slideshow a ser criado.
    :param video_type: Formato do arquivo de vídeo a ser criado.
    :param std_dimension: Resolução do arquivo de vídeo a ser criado.
    :param fotos_filename: Lista com os nomes dos arquivos a serem usadas para criação 
        do slideshow. Arquivos que serão buscados do path informado 'self.dir_fotos'. 
        Caso não seja informado esta lista, todas as fotos do diretório serão utilizadas.
    """

    STD_DIMENSIONS =  {
        "360p": (480, 360),
        "480p": (640, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4k": (3840, 2160),
    }

    VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            #'mp4-h': cv2.VideoWriter_fourcc(*'H264'),
            #'mp4': cv2.VideoWriter_fourcc(*'X264'),
            'mp4': cv2.VideoWriter_fourcc(*'avc1'),
    }

    def __init__(self, dir_fotos=None, dir_video=None, video_filename=None, 
                    video_type='mp4', std_dimension='720p', fotos_filename=None,
                    segundos_por_img=5):
        self.dir_fotos = dir_fotos
        self.video_filename = video_filename
        self.dir_video = dir_video
        self.fotos_filename = fotos_filename
        self.absolute_path = '{path}/{file}.{ext}'.format(path=dir_video, file=video_filename,ext=video_type)

        self.fps = 24
        self.segundos_por_img = segundos_por_img

        self.video_type = video_type
        self.videowriter_type = Slideshow.VIDEO_TYPE[video_type]

        self.std_dimension = std_dimension
        self.dimensao = Slideshow.STD_DIMENSIONS[std_dimension]

        self.fotos_inseridas = 0
        self.terminado = False


    def _criar_video_writer(self):
         return cv2.VideoWriter(
                    self.absolute_path, 
                    self.videowriter_type,
                    self.fps, 
                    self.dimensao
                )


    def criar(self):
        out = self._criar_video_writer()
        
        if  self.fotos_filename is None:
            self.fotos_filename = os.listdir(self.dir_fotos)

        for file_name in self.fotos_filename:
            try:
                path_foto = '{path}/{file}'.format(path=self.dir_fotos, file=file_name)
                self.fotos_inseridas += 1

                ''' IMAGEM COM ESPAÇO NO NOME NÃO ESTÁ ABRINDO'''
                img = cv2.imread(path_foto)

                if img is None: 
                    continue

                img_fundo = self._criar_fundo()
                imagem = self._criar_imagem_slide(img_fundo, img)

                for _ in range(self.segundos_por_img * self.fps):
                    out.write(imagem)
            except:
                print("ERRO: Erro ao abrir imagem '%s'"%file_name)


        out.release()
        self.terminado = True


    def _criar_fundo(self, cor=255):
        '''
        Cria uma matriz tridimensional que será o fundo do slideshow. 
        O video só é possivel ser criado a partir de imagens do mesmo tamanho,
        por isso, O fundo das imagens devem ser padronizados.
        '''
        return np.ones((self.dimensao[1], self.dimensao[0],  3)) * cor


    def _criar_imagem_slide(self, img_fundo, img):
        ''' Copia a imagem para uma área selecionada na imagem de fundo. '''

        margem = 50
        height_max = self.dimensao[1] - margem
        width_max = self.dimensao[0] - margem

        h, w = img.shape[:2]
        imagem = None

        # Se o altura for maior que a largura, redimensiona pela altura.
        # É necessário redimensionar pela altura se a imagem for quadrada, neste caso.
        # Pois a imagem de fundo utilizada é horizontal, e ajustando a imagem de acordo com a 
        # altura, menor dimensao do fundo, fará com que a largura atribida à imagem não exceda 
        # a largura do fundo.
        if h >= w:
            imagem = self._redimensionar_imagem(img, height = height_max) 
        else:
            imagem = self._redimensionar_imagem(img, width = width_max)

        h, w = imagem.shape[:2]

        ''' Verificar se isso é necessário mesmo'''
        if h > img_fundo.shape[0]:
            imagem = self._redimensionar_imagem(imagem, height = img_fundo.shape[0] - margem)
        if w > img_fundo.shape[1]:
            imagem = self._redimensionar_imagem(imagem, width = img_fundo.shape[1] - margem)

        h, w = imagem.shape[:2]
        
        # define a centralizacão da imagem na imagem de fundo
        inicio_y = math.ceil((img_fundo.shape[0] - h)/2)
        inicio_x = math.ceil((img_fundo.shape[1] - w)/2)
        termino_y = inicio_y+h
        termino_x = inicio_x+w

        # 'Cola' a imagem na localização definida
        img_fundo[ inicio_y:termino_y , inicio_x:termino_x ] = imagem
        cv2.imwrite('temp.jpg', img_fundo)

        return cv2.imread('temp.jpg')


    def _redimensionar_imagem(self, imagem, width = None, height = None):
        
        if not width and not height:
            return imagem

        dim = None
        h, w = imagem.shape[:2]
        
        # Se width é none, calcula o width com base no height.
        if not width:
            r = height / float(h)
            dim = (int(w * r), height)
        # Se não, calcula o height com base no width.
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(imagem, dim, interpolation=cv2.INTER_AREA)