from direct.showbase.ShowBase   import ShowBase
from direct.task                import Task
from panda3d.core               import Geom, GeomNode
from panda3d.core               import GeomVertexFormat, GeomVertexWriter, GeomVertexData
from panda3d.core               import GeomTristrips
from panda3d.core               import PointLight
from panda3d.core               import VBase4
from panda3d.core               import SamplerState
from panda3d.core               import Shader
import random

class Grid(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.cols = 100
        self.rows = 100

        base.disableMouse()
        base.setFrameRateMeter(True)
        self.cameraHeight = 13
        self.camera.set_pos(self.cols/2,-30,self.cameraHeight)
        self.camera.look_at(self.cols/2,300,0)

        plights = []

        for i in range(0,int(self.cols/5),2):
            plight = PointLight("plight")
            plight.setColor(VBase4(1, 1, 1, 1))
            plights.append(plight)
            plights[i] = self.render.attachNewNode(plight)
            x,y,z = self.camera.get_pos()
            plights[i].setPos(self.cols/2+((i-int(i/2))*10),y+20,5)
            self.render.set_light(plights[i])

            plight = PointLight("plight")
            plight.setColor(VBase4(1, 1, 1, 1))
            plights.append(plight)
            plights[i+1] = self.render.attachNewNode(plight)
            x,y,z = self.camera.get_pos()
            plights[i+1].setPos(self.cols/2+((i-int(i/2))*10),y+20,10)
            self.render.set_light(plights[i+1])

        self.plights = plights

        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('name', format, Geom.UHStatic)
        vdata.setNumRows(self.cols*self.rows)
        self.vertex = GeomVertexWriter(vdata, 'vertex')
        self.color = GeomVertexWriter(vdata, 'color')

        pz = [random.uniform(-1,1)]
        for i in range(self.rows):
            pz.append(random.uniform(pz[i-1]-1,pz[i]+1))
        for y in range(0,self.rows):
            for x in range(0,self.cols):
                nz1 = random.uniform(pz[x]-1,pz[x]+1)
                nz2 =random.uniform(pz[x-1]-1,pz[x-1]+1)
                nz3 = random.uniform(pz[x+1] - 1, pz[x + 1] + 1)
                nz = (nz1 + nz2 + nz3) / 3
                self.vertex.add_data3f((x,y+1,nz))
                self.vertex.add_data3f((x,y,pz[x]))
                if nz < -5:
                    self.color.add_data4f(0.2,0.1,0,1)
                elif nz < -3:
                    self.color.add_data4f(0,0.2,0.1,1)
                elif nz < 0:
                    self.color.add_data4f(0,0.4,0.2,1)
                elif nz < 2:
                    self.color.add_data4f(0.4,0.4,0.4,1)
                else:
                    self.color.add_data4f(1,1,1,1)
                if nz < -5:
                    self.color.add_data4f(0.2, 0.1, 0, 1)
                elif nz < -3:
                    self.color.add_data4f(0, 0.2, 0.1,1)
                elif pz[x] < 0:
                    self.color.add_data4f(0,0.4,0.2,1)
                elif pz[x] < 2:
                    self.color.add_data4f(0.4,0.4,0.4,1)
                else:
                    self.color.add_data4f(1,1,1,1)
                pz[x] = nz
                print (nz)
        self.pz = pz

        geom = Geom(vdata)
        for y in range(0, self.rows):
            prim = GeomTristrips(Geom.UH_static)
            prim.addVertex(y*self.cols*2)
            prim.add_next_vertices((self.cols*2)-1)
            prim.close_primitive()
            geom.addPrimitive(prim)

        nodeTris = GeomNode("TriStrips")
        nodeTris.addGeom(geom)
        self.nodeTrisPath = self.render.attachNewNode(nodeTris)
        self.task_mgr.add(self.moveForwardTask,"moveForwardTask")

        self.vdata = vdata
        self.newNodePath = []
        self.counter = 0
        self.rows1 = self.rows

        skybox = self.loader.loadModel("models/skybox.bam")
        skybox.reparent_to(self.render)
        skybox.set_scale(20000)

        skybox_texture = self.loader.loadTexture("textures/dayfair.jpg")
        skybox_texture.set_minfilter(SamplerState.FT_linear)
        skybox_texture.set_magfilter(SamplerState.FT_linear)
        skybox_texture.set_wrap_u(SamplerState.WM_repeat)
        skybox_texture.set_wrap_v(SamplerState.WM_mirror)
        skybox_texture.set_anisotropic_degree(16)
        skybox.set_texture(skybox_texture)

        skybox_shader = Shader.load(Shader.SL_GLSL, "skybox.vert.glsl", "skybox.frag.glsl")
        skybox.set_shader(skybox_shader)

    def moveForwardTask(self,task):
        change = 0.7
        self.counter = self.counter+change
        x,y,z = self.camera.get_pos()
        self.camera.set_pos(x,y+change,z)
        for i in range(0,len(self.plights)):
            x,y,z = self.plights[i].get_pos()
            self.plights[i].set_pos(x,y+change,z)
            self.render.set_light(self.plights[i])

        if y>self.rows1:
            self.nodeTrisPath.removeNode()

        if self.counter >= 1:
            if y > self.rows1:
                self.newNodePath[0].removeNode()
                del self.newNodePath[0]
            self.counter = self.counter - 1
            for x in range(0, self.cols):
                nz1 = random.uniform(self.pz[x] - 1, self.pz[x] + 1)
                nz2 = random.uniform(self.pz[x - 1] - 1, self.pz[x - 1] + 1)
                nz3 = random.uniform(self.pz[x + 1] - 1, self.pz[x + 1] + 1)
                nz = (nz1 + nz2 + nz3) / 3
                self.vertex.add_data3f((x, self.rows + 1, nz))
                self.vertex.add_data3f((x, self.rows, self.pz[x]))
                if nz < -5:
                    self.color.add_data4f(0.2, 0.1, 0, 1)
                elif nz < -3:
                    self.color.add_data4f(0, 0.2, 0.1, 1)
                elif nz < 0:
                    self.color.add_data4f(0, 0.4, 0.2, 1)
                elif nz < 4:
                    self.color.add_data4f(0.4, 0.4, 0.4, 1)
                else:
                    self.color.add_data4f(1, 1, 1, 1)
                if nz < -5:

                    self.color.add_data4f(0.2, 0.1, 0, 1)
                elif nz < -3:
                    self.color.add_data4f(0, 0.2, 0.1, 1)
                elif self.pz[x] < 0:
                    self.color.add_data4f(0, 0.4, 0.2, 1)
                elif self.pz[x] < 4:
                    self.color.add_data4f(0.4, 0.4, 0.4, 1)
                else:
                    self.color.add_data4f(1, 1, 1, 1)
                self.pz[x] = nz
                print (nz)
            geom = Geom(self.vdata)
            prim = GeomTristrips(Geom.UH_static)
            prim.addVertex(self.cols*2*self.rows)
            prim.add_next_vertices((self.cols * 2)-1)
            prim.close_primitive()
            geom.addPrimitive(prim)
            node = GeomNode("TriStrips")
            node.addGeom(geom)
            self.newNodePath.append(self.render.attachNewNode(node))
            self.rows = self.rows + 1
        return Task.cont

grid = Grid()
grid.run()