# 이것은 각 상태들을 객체로 구현한 것임.

from pico2d import load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, get_time, SDLK_RIGHT, SDLK_LEFT
import math


# define event check functions
def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == 'TIME_OUT'


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def a_down(e):
    return e[0] == 'INPUT' and SDL_KEYDOWN and e[1].key == ord('a')
class AutoRun:

    @staticmethod
    def enter(boy, e):
        boy.dir = 1
        boy.action = 1
        boy.speed = 10
        boy.autorun_start_time = get_time()

    @staticmethod
    def exit(boy, e):
        boy.speed = 5

    @staticmethod
    def do(boy):
        boy.speed += 0.08
        boy.frame = (boy.frame + 1) % 8

        if (boy.x > 780):
            boy.dir = -1
            boy.action = 0
        elif (boy.x < 10):
            boy.dir = 1
            boy.action = 1
        boy.x += boy.dir * boy.speed

        if get_time() - boy.autorun_start_time > 5:
            boy.state_machine.handle_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100,
                            boy.x, boy.y+30, 200, 200)
        pass


class Idle:

    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.dir = 0
        boy.frame = 0
        boy.idle_start_time = get_time()

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.idle_start_time > 3:
            boy.state_machine.handle_event(('TIME_OUT', 0))


    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100,
                            boy.x, boy.y)
        pass


class Sleep:

    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        print('드르렁')

    @staticmethod
    def draw(boy):
        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100,
                                          -math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100,
                                          math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100)


class Run:

    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):  # 오른쪽으로 RUN
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e):  # 왼쪽으로 RUN
            boy.dir, boy.action = -1, 0
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100,
                            boy.x, boy.y)
        pass


class StateMachine:
    def __init__(self, boy):
        self.cur_state = Idle
        self.boy = boy
        self.transitions = {
            Sleep: {space_down: Idle, right_down: Run, left_down: Run, right_up: Run, left_up: Run, a_down: AutoRun},
            Idle: {time_out: Sleep, right_down: Run, left_down: Run, right_up: Run, left_up: Run, a_down: AutoRun},
            Run: {space_down: Idle, right_down: Run, left_down: Run, right_up: Idle, left_up: Idle, a_down: AutoRun},
            AutoRun: {time_out: Idle}
        }

    def start(self):
        self.cur_state.enter(self.boy, ('NONE', 0))

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True
        return False

    def update(self):
        self.cur_state.do(self.boy)

    def draw(self):
        self.cur_state.draw(self.boy)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        # control_boy.py에서 호출함
        self.state_machine.handle_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()
