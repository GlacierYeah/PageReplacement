import logging
import threading
from flask import Flask, render_template, request, jsonify
from algorithms import FIFO, LRU, OPT, LFU
import queue
import time

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 存储算法实例
algorithms = {
    'fifo': None,
    'lru': None,
    'opt': None,
    'lfu': None
}

# 线程锁，用于保护共享资源
lock = threading.Lock()

def process_page_worker(algorithm_name, page, memory_size, use_quick_table, time_settings, future_sequence, result_queue):
    try:
        # 参数验证
        if page is None:
            raise ValueError("页面号不能为空")
        if memory_size is None or memory_size <= 0:
            raise ValueError("内存大小必须大于0")
        if time_settings is None:
            time_settings = {
                'memoryAccessTime': 100,
                'pageFaultTime': 10000,
                'quickTableTime': 20
            }
        if future_sequence is None:
            future_sequence = []

        logger.debug(f"Processing page {page} for {algorithm_name} with memory_size={memory_size}, use_quick_table={use_quick_table}")
        logger.debug(f"Time settings: {time_settings}")
        logger.debug(f"Future sequence: {future_sequence}")

        with lock:
            # 如果算法实例不存在，创建新的实例
            if algorithms[algorithm_name] is None:
                logger.debug(f"Creating new {algorithm_name} algorithm instance")
                if algorithm_name == 'fifo':
                    algorithms[algorithm_name] = FIFO(memory_size, use_quick_table)
                elif algorithm_name == 'lru':
                    algorithms[algorithm_name] = LRU(memory_size, use_quick_table)
                elif algorithm_name == 'opt':
                    algorithms[algorithm_name] = OPT(memory_size, use_quick_table)
                elif algorithm_name == 'lfu':
                    algorithms[algorithm_name] = LFU(memory_size, use_quick_table)
            
            # 获取算法实例
            algorithm = algorithms[algorithm_name]
            if algorithm is None:
                raise ValueError(f"无法创建{algorithm_name}算法实例")
            
            # 处理页面
            logger.debug(f"Processing page {page} with {algorithm_name}")
            is_page_fault, replaced_page, access_time = algorithm.process_page(page, time_settings, future_sequence)
            
            # 获取算法状态
            state = algorithm.get_state()
            if state is None:
                raise ValueError(f"无法获取{algorithm_name}算法状态")
            
            logger.debug(f"Algorithm state: {state}")
            
            # 将结果放入队列
            result = {
                'status': 'success',
                'algorithm': algorithm_name,
                'result': {
                    'type': 'page_fault_replace' if is_page_fault and replaced_page else 
                           'page_fault_new' if is_page_fault else 
                           'memory_hit',
                    'page': page,
                    'replaced_page': replaced_page,
                    'memory': state.get('memory', []),
                    'quick_table': state.get('quick_table', []),
                    'time': access_time
                },
                'state': {
                    'memory': state.get('memory', []),
                    'quick_table': state.get('quick_table', []),
                    'faults': state.get('faults', 0),
                    'time': state.get('total_time', 0),
                    'step': state.get('step', 0)
                }
            }
            logger.debug(f"Sending result: {result}")
            result_queue.put(result)
            
    except Exception as e:
        logger.error(f"Error in {algorithm_name} algorithm: {str(e)}", exc_info=True)
        result_queue.put({
            'status': 'error',
            'algorithm': algorithm_name,
            'error': str(e)
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset():
    try:
        global algorithms
        with lock:
            # 重置所有算法实例
            algorithms = {
                'fifo': None,
                'lru': None,
                'opt': None,
                'lfu': None
            }
            logger.info("Successfully reset all algorithms")
            return jsonify({
                'status': 'success',
                'message': '所有算法已重置'
            })
    except Exception as e:
        logger.error(f"Error resetting algorithms: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'重置算法时发生错误：{str(e)}'
        }), 500

@app.route('/process_page', methods=['POST'])
def process_page():
    try:
        data = request.get_json()
        if data is None:
            raise ValueError("请求数据不能为空")

        page = data.get('page')
        if page is None:
            raise ValueError("页面号不能为空")

        memory_size = data.get('memory_size', 3)
        use_quick_table = data.get('use_quick_table', False)
        time_settings = data.get('time_settings', {
            'memoryAccessTime': 100,
            'pageFaultTime': 10000,
            'quickTableTime': 20
        })
        future_sequence = data.get('future_sequence', [])
        
        logger.debug(f"Processing page {page} with memory_size={memory_size}, use_quick_table={use_quick_table}")
        
        # 创建结果队列
        result_queue = queue.Queue()
        
        # 创建并启动所有算法的线程
        threads = []
        for algorithm_name in ['fifo', 'lru', 'opt', 'lfu']:
            thread = threading.Thread(
                target=process_page_worker,
                args=(algorithm_name, page, memory_size, use_quick_table, time_settings, future_sequence, result_queue)
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 收集所有结果
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # 检查是否有错误
        errors = [r for r in results if r['status'] == 'error']
        if errors:
            error_messages = [f"{e['algorithm']}: {e['error']}" for e in errors]
            return jsonify({
                'status': 'error',
                'error': '处理页面时发生错误：' + '; '.join(error_messages)
            })
        
        # 返回成功结果
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing page: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
