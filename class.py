import streamlit as st
import os
import json

UPLOADS_DIR = "uploads"
CLASSES_FILE = "classes.json"
TEACHERS_FILE = "teachers.json"
STUDENTS_FILE = "students.json"

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

# 创建一个示例班级文件，包含初始的班级信息
initial_classes = {"1": "1班", "2": "2班", "3": "3班", "4": "4班级", "5": "5班级",
                   "6": "6班", "7": "7班", "8": "8班级", "9": "9班级", "10": "10班级",
                   "11": "11班", "12": "12班", "13": "13班级", "14": "14班级", "15": "15班级",
                   "16": "16班", "17": "17班", "18": "18班级", "19": "19班级", "20": "20班级"}

with open(CLASSES_FILE, "w") as classes_file:
    json.dump(initial_classes, classes_file)

# 创建一个示例教师文件，包含初始的教师信息，包括负责的班级
initial_teachers = {"T1": {"name": "付", "classes": ["4", "7", "12", "13", "15"]},
                    "T2": {"name": "温", "classes": ["3", "11", "17"]},
                    "T3": {"name": "何", "classes": ["1", "2", "5", "19", "20"]},
                    "T4": {"name": "刘", "classes": ["6", "8", "9", "10", "14", "16", "18"]}
                    }
with open(TEACHERS_FILE, "w") as teachers_file:
    json.dump(initial_teachers, teachers_file)

# 创建一个示例学生文件，包含初始的学生信息，每个班级有30个学生
initial_students = {str(i): [f"学生{i * 100 + j}" for j in range(1, 31)] for i in range(1, 21)}
with open(STUDENTS_FILE, "w") as students_file:
    json.dump(initial_students, students_file)


def main():
    st.title("仲元小天才作业系统")
    user_type = st.radio("选择用户类型:", ["老师", "学生"])

    if user_type == "老师":
        teacher_info = st.text_input("输入教师编号和姓名，格式为Tn:+姓氏:")
        if is_valid_teacher(teacher_info):
            show_teacher_interface(teacher_info)
    elif user_type == "学生":
        show_student_interface()


def is_valid_teacher(teacher_info):
    # 检查老师编号是否存在于教师文件中
    teachers = load_teachers()
    teacher_info = teacher_info.strip().split(":")
    return len(teacher_info) == 2 and teacher_info[0] in teachers


def show_teacher_interface(teacher_info):
    st.header("控制界面")

    # 获取教师信息
    teacher_id, teacher_name = teacher_info.strip().split(":")
    st.write(f"欢迎，{teacher_name}！")

    # 获取负责的班级
    classes = get_teacher_classes(teacher_id)
    st.write(f"当前负责的班级: {', '.join(classes)}")

    # 创建或删除班级
    action = st.selectbox("选择操作:", ["创建班级", "删除班级", "查看学生名单"])
    if action == "创建班级":
        new_class_name = st.text_input("输入新班级名称:")
        if st.button("创建班级"):
            create_class(teacher_id, new_class_name)
    elif action == "删除班级":
        class_to_delete = st.selectbox("选择要删除的班级:", classes)
        if st.button("删除班级"):
            delete_class(teacher_id, class_to_delete)
    elif action == "查看学生名单":
        class_to_view = st.selectbox("选择要查看学生名单的班级:", classes)
        show_students_table(class_to_view)

# 新增函数用于显示学生名单表格
def show_students_table(class_to_view):
    students = load_students()
    class_students = students.get(class_to_view, [])

    if class_students:
        st.subheader(f"班级 {class_to_view} 的学生名单:")
        student_table_data = {"学生姓名": class_students}
        st.table(student_table_data)
    else:
        st.warning("该班级还没有学生名单。")

def load_teachers():
    # 从教师文件中加载教师信息
    if os.path.exists(TEACHERS_FILE):
        with open(TEACHERS_FILE, "r") as teachers_file:
            teachers = json.load(teachers_file)
        return teachers
    else:
        return {}


def get_teacher_classes(teacher_id):
    # 获取教师负责的班级
    teachers = load_teachers()
    return teachers.get(teacher_id, {}).get("classes", [])


def process_teacher_list(teacher_list):
    st.subheader("上传的教师名单内容:")
    content = teacher_list.read()
    st.text(content)


def show_student_interface():
    st.header("学生界面")

    # 上传Python文件
    st.warning("请上传一个Python文件 (.py)")
    uploaded_file = st.file_uploader("上传Python文件", type=["py"])
    if uploaded_file is not None:
        process_uploaded_file(uploaded_file)


def process_uploaded_file(uploaded_file):
    file_path = os.path.join(UPLOADS_DIR, uploaded_file.name)
    with open(file_path, "wb") as file:
        file.write(uploaded_file.read())

    st.subheader("上传的Python文件内容:")
    st.code(open(file_path, "r").read(), language="python")


def load_classes():
    # 从班级文件中加载班级信息
    if os.path.exists(CLASSES_FILE):
        with open(CLASSES_FILE, "r") as classes_file:
            classes = json.load(classes_file)
        return classes
    else:
        return {}


def save_classes(classes):
    # 将班级信息保存到文件
    with open(CLASSES_FILE, "w") as classes_file:
        json.dump(classes, classes_file)


def create_class(teacher_id, new_class_name):
    # 仅允许教师删除或增加他们自己负责的班级
    classes = load_classes()
    teachers = load_teachers()

    if teacher_id in teachers:
        # 添加新班级
        new_class_id = str(max(map(int, classes.keys())) + 1)
        classes[new_class_id] = new_class_name
        teachers[teacher_id]["classes"].append(new_class_id)

        save_classes(classes)
        save_teachers(teachers)

        st.success(f"成功创建新班级: {new_class_name}")
    else:
        st.warning("您只能创建您负责的班级！")
    update_students_for_class(new_class_id)
def update_students_for_class(class_id):
    students = load_students()
    students[class_id] = []
    save_students(students)
def save_students(students):
    with open(STUDENTS_FILE, "w") as students_file:
        json.dump(students, students_file)
def delete_class(teacher_id, class_to_delete):
    # 仅允许教师删除或增加他们自己负责的班级
    classes = load_classes()
    teachers = load_teachers()

    if teacher_id in teachers and class_to_delete in classes.values():
        class_id_to_delete = next((k for k, v in classes.items() if v == class_to_delete), None)

        # 删除班级
        del classes[class_id_to_delete]
        teachers[teacher_id]["classes"].remove(class_id_to_delete)

        save_classes(classes)
        save_teachers(teachers)

        st.success(f"成功删除班级: {class_to_delete}")
    else:
        st.warning("您只能删除您负责的班级！")


def show_students(class_id):
    # 查看班级学生名单
    students = load_students()
    class_students = students.get(class_id, [])

    st.subheader(f"{class_id}班学生名单:")
    st.write("\n".join(class_students))


def load_students():
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, "r") as students_file:
            students = json.load(students_file)
        return students
    else:
        return {}


def save_teachers(teachers):
    # 将教师信息保存到文件
    with open(TEACHERS_FILE, "w") as teachers_file:
        json.dump(teachers, teachers_file)


if __name__ == "__main__":
    main()
