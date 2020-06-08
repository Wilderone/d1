import requests
import sys
import re


auth_params = {
'key':'ccda1fc50ba2ab8bde6f55be70565bff',
'token' : '5635298a872e377f3a8c0aae8962847a46f8d01979de46e9ed1a6140252f1a01',}
base_url = "https://api.trello.com/1/{}"
board_id = 'q26gQzn1'
actions = {'1. Изменить имя задачи','2. Переместить задачу','3. Удалить задачу'}
data = {}
columns_all={}

def input_name(text='Выберите имя задачи:'):
    name= input(text)
    if name:
        return name

    else:

        input_name('Пожалуйста введите имя задачи:')


def input_num(slovar,text=''):
    num = input(text)
    if num.isnumeric():
        if 0 < int(num) <= len(slovar):
            return int(num)
        else:
            print('Пожалуйста введите число  от 1 до {}'.format(len(slovar)))
            input_num(slovar)
    else:
        print('Пожалуйста введите число  от 1 до {}'.format(len(slovar)))
        input_num(slovar)

def read():
    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        print(column['name'])
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'])




def check_task_name(name):

    i = 1
    x = 1
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in column_data:
        #словарь всех колонок
        columns_all [x]=[column['name'],column['id']]
        x+=1
        #получаем список задач в каждой колонке

        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()

        for task in task_data:

            if task['name'] == name:
                data[i] = [column['name'], column['id'],task['id'],task['dateLastActivity']]
                i+=1

    if len(data) == 0:
        print('Задача с таким именем не найдена, создадим новую')
        return True

    else:
        print ('Задача {} есть в колонке(ах):'.format(name))
        for a,b in data.items():
            print ('{}. {}  дата создания - {}'.format(a,b[0],b[3]))
        return False


def create_list (name):
    requests.post(base_url.format('boards')+ '/' + board_id + '/lists', data={'name': name, **auth_params})


def update():
    print ('Обновляем количество задач в колонках')
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    for column in column_data:

        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()

        # если нет задач, добавляем (0)

        if not task_data:

            if not re.search(r'\(\d+\)', column['name']):
                requests.put(base_url.format('list') + '/' + column['id'],
                             data={'name': column['name'] + '(0)', **auth_params})


            continue
        else:

            #если уже указано количество удаляем и ставим новое

            if re.findall(r'\(\d+\)', column['name']):

                name = re.sub(r'\(\d+\)', '' ,column['name'])

                requests.put(base_url.format('list') + '/' + column['id'],
                             data={'name': name + '('+str(len(task_data))+')', **auth_params})

            else:
            # добавляем количество задач
                requests.put(base_url.format('list') + '/' + column['id'],
                     data={'name': column['name'] + '('+str(len(task_data))+')', **auth_params})
  
def move_task(name, task_id, new_column_id):

    result = requests.put(base_url.format('cards') + '/' + task_id + '/idList',
                 data={'value': new_column_id, **auth_params})
    if result:
        print('Задача {} успешно перемещена.'.format(name))
    else:
        print('Что-то пошло не так - {}'.format(result))


def del_task(name,task_id):

    result = requests.delete(base_url.format('cards') + '/' + task_id,
                 data={**auth_params})
    if result:
        print('Задача {} успешно удалена.'.format(name))
    else:
        print('Что-то пошло не так - {}'.format(result))


def update_task(name,id_column,new_name):
    column_tasks = requests.get(base_url.format('lists') + '/' + id_column + '/cards', params=auth_params).json()
    for task in column_tasks:
        if task['name'] == name:
            task_id = task['id']
            break
    result = requests.put(base_url.format('cards') + '/' + task_id,
                 data={'name': new_name, **auth_params})
    if result:
        print('Задача {} успешно обновленна.'.format(new_name))
    else:
        print('Что-то пошло не так - {}'.format(result))

def task():

    columns ={}
    i = 1
    name = input_name()
    if check_task_name(name):
        column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
        for column in column_data:

            columns[i]=[column['name'], column['id']]
            i+=1

        for a, b in columns.items():
            print('{}. {}'.format(a, b[0]))

        num = input_num(columns,'Выберите колонку в которую добавить задачу:')

        result = requests.post(base_url.format('cards'), data={'name': name, 'idList': columns[num][1], **auth_params})
        if result:
            print('Задача {} успешно добавлена.'.format(name))
        else:
            print('Что-то пошло не так - {}'.format(result))
    else:
        #выбираем номер задачи с которой хотим работать
        if len(data) == 1:
            task_id = data[1][2]

        else:
            num_task = input_num(data, 'Введите номер задачи:')

            task_id = data[num_task][2]


        print('\n Выберите что хотите сделать с задачей "{}".'.format(name))
        for a in actions:
            print (a)
        num = input_num(actions,'Введите вариант:')
        if num == 3:
            del_task(name,task_id)
        if num == 1:
            new_name = input_name('Пожалуйста введите НОВОЕ имя задачи:')
            update_task(name, data[1][1],new_name)
        if num == 2:
            for a, b in columns_all.items():

                print('{}. {}'.format(a, b[0]))
            new_column = input_num(actions,'Выбирите в какую колонку переместить задачу {}:'.format(name))
            move_task(name, task_id, columns_all[new_column][1])

    update()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print ('Параметры запуска\n 1. python api.py - вывод справки\n 2. python api.py read - вывод списка задач \n 3. python api.py update - обновление количества задач в списке \n 4. python api.py task- создание\редактирование\удаление\перемещение задачи \n 5. python api.py create_list {name} - создание колонки')
    elif sys.argv[1] == 'read':
        read()
    elif sys.argv[1] == 'update':
        update()
    elif sys.argv[1] == 'task':
        task()
    elif sys.argv[1] == 'create_list':
        create_list(sys.argv[2], sys.argv[3])


