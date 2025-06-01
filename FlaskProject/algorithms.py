class PageReplacementAlgorithm:
    def __init__(self, memory_size, use_quick_table=False):
        self.memory_size = memory_size
        self.use_quick_table = use_quick_table
        self.memory = []
        self.quick_table = []
        self.faults = 0
        self.total_time = 0
        self.step = 0
        self.history = []

    def reset(self):
        self.memory = []
        self.quick_table = []
        self.faults = 0
        self.total_time = 0
        self.step = 0
        self.history = []

    def get_state(self):
        return {
            'memory': self.memory.copy(),
            'quick_table': self.quick_table.copy(),
            'faults': self.faults,
            'total_time': self.total_time,
            'step': self.step
        }

class FIFO(PageReplacementAlgorithm):
    def process_page(self, page, time_settings, future_sequence=None):
        is_page_fault = False
        replaced_page = None
        access_time = 0

        # 检查快表
        if self.use_quick_table and page in self.quick_table:
            access_time = time_settings['quickTableTime']
            self.history.append({
                'type': 'quick_table_hit',
                'page': page,
                'time': access_time
            })
        else:
            # 检查内存
            if page in self.memory:
                access_time = time_settings['memoryAccessTime']
                self.history.append({
                    'type': 'memory_hit',
                    'page': page,
                    'time': access_time
                })
            else:
                # 缺页中断
                is_page_fault = True
                access_time = time_settings['pageFaultTime']
                self.faults += 1

                if len(self.memory) < self.memory_size:
                    self.memory.append(page)
                    self.history.append({
                        'type': 'page_fault_new',
                        'page': page,
                        'time': access_time
                    })
                else:
                    replaced_page = self.memory.pop(0)
                    self.memory.append(page)
                    self.history.append({
                        'type': 'page_fault_replace',
                        'page': page,
                        'replaced_page': replaced_page,
                        'time': access_time
                    })

                # 更新快表
                if self.use_quick_table:
                    if page not in self.quick_table:
                        if len(self.quick_table) >= min(4, self.memory_size):
                            self.quick_table.pop(0)
                        self.quick_table.append(page)

        self.total_time += access_time
        self.step += 1
        return is_page_fault, replaced_page, access_time

class LRU(PageReplacementAlgorithm):
    def __init__(self, memory_size, use_quick_table=False):
        super().__init__(memory_size, use_quick_table)
        self.access_times = {}

    def reset(self):
        super().reset()
        self.access_times = {}

    def process_page(self, page, time_settings, future_sequence=None):
        is_page_fault = False
        replaced_page = None
        access_time = 0

        # 检查快表
        if self.use_quick_table and page in self.quick_table:
            access_time = time_settings['quickTableTime']
            self.access_times[page] = self.step
            self.history.append({
                'type': 'quick_table_hit',
                'page': page,
                'time': access_time
            })
        else:
            # 检查内存
            if page in self.memory:
                access_time = time_settings['memoryAccessTime']
                self.access_times[page] = self.step
                self.history.append({
                    'type': 'memory_hit',
                    'page': page,
                    'time': access_time
                })
            else:
                # 缺页中断
                is_page_fault = True
                access_time = time_settings['pageFaultTime']
                self.faults += 1
                self.access_times[page] = self.step

                if len(self.memory) < self.memory_size:
                    self.memory.append(page)
                    self.history.append({
                        'type': 'page_fault_new',
                        'page': page,
                        'time': access_time
                    })
                else:
                    # 找到最近最少使用的页面（访问时间最早）
                    lru_page = min(self.memory, key=lambda p: self.access_times.get(p, float('inf')))
                    replaced_page = lru_page
                    self.memory.remove(lru_page)
                    self.memory.append(page)
                    self.history.append({
                        'type': 'page_fault_replace',
                        'page': page,
                        'replaced_page': replaced_page,
                        'time': access_time
                    })

                # 更新快表
                if self.use_quick_table:
                    if page not in self.quick_table:
                        if len(self.quick_table) >= min(4, self.memory_size):
                            self.quick_table.pop(0)
                        self.quick_table.append(page)

        self.total_time += access_time
        self.step += 1
        return is_page_fault, replaced_page, access_time

class OPT(PageReplacementAlgorithm):
    def process_page(self, page, time_settings, future_sequence):
        is_page_fault = False
        replaced_page = None
        access_time = 0

        # 检查快表
        if self.use_quick_table and page in self.quick_table:
            access_time = time_settings['quickTableTime']
            self.history.append({
                'type': 'quick_table_hit',
                'page': page,
                'time': access_time
            })
        else:
            # 检查内存
            if page in self.memory:
                access_time = time_settings['memoryAccessTime']
                self.history.append({
                    'type': 'memory_hit',
                    'page': page,
                    'time': access_time
                })
            else:
                # 缺页中断
                is_page_fault = True
                access_time = time_settings['pageFaultTime']
                self.faults += 1

                if len(self.memory) < self.memory_size:
                    self.memory.append(page)
                    self.history.append({
                        'type': 'page_fault_new',
                        'page': page,
                        'time': access_time
                    })
                else:
                    # 找到将来最晚使用或不再使用的页面
                    future_uses = {}
                    for i, future_page in enumerate(future_sequence):
                        if future_page in self.memory and future_page not in future_uses:
                            future_uses[future_page] = i

                    # 对于内存中但未来不会使用的页面，设置一个很大的值
                    for mem_page in self.memory:
                        if mem_page not in future_uses:
                            future_uses[mem_page] = float('inf')

                    # 选择最晚使用的页面
                    opt_page = max(self.memory, key=lambda p: future_uses.get(p, float('inf')))
                    replaced_page = opt_page
                    self.memory.remove(opt_page)
                    self.memory.append(page)
                    self.history.append({
                        'type': 'page_fault_replace',
                        'page': page,
                        'replaced_page': replaced_page,
                        'time': access_time
                    })

                # 更新快表
                if self.use_quick_table:
                    if page not in self.quick_table:
                        if len(self.quick_table) >= min(4, self.memory_size):
                            self.quick_table.pop(0)
                        self.quick_table.append(page)

        self.total_time += access_time
        self.step += 1
        return is_page_fault, replaced_page, access_time

class LFU(PageReplacementAlgorithm):
    def __init__(self, memory_size, use_quick_table=False):
        super().__init__(memory_size, use_quick_table)
        self.frequency = {}

    def reset(self):
        super().reset()
        self.frequency = {}

    def process_page(self, page, time_settings, future_sequence=None):
        is_page_fault = False
        replaced_page = None
        access_time = 0

        # 初始化频次
        if page not in self.frequency:
            self.frequency[page] = 0

        # 检查快表
        if self.use_quick_table and page in self.quick_table:
            access_time = time_settings['quickTableTime']
            self.frequency[page] += 1
            self.history.append({
                'type': 'quick_table_hit',
                'page': page,
                'frequency': self.frequency[page],
                'time': access_time
            })
        else:
            # 检查内存
            if page in self.memory:
                access_time = time_settings['memoryAccessTime']
                self.frequency[page] += 1
                self.history.append({
                    'type': 'memory_hit',
                    'page': page,
                    'frequency': self.frequency[page],
                    'time': access_time
                })
            else:
                # 缺页中断
                is_page_fault = True
                access_time = time_settings['pageFaultTime']
                self.faults += 1
                self.frequency[page] += 1

                if len(self.memory) < self.memory_size:
                    self.memory.append(page)
                    self.history.append({
                        'type': 'page_fault_new',
                        'page': page,
                        'frequency': self.frequency[page],
                        'time': access_time
                    })
                else:
                    # 找到使用频次最少的页面
                    lfu_page = min(self.memory, key=lambda p: self.frequency.get(p, 0))
                    replaced_page = lfu_page
                    self.memory.remove(lfu_page)
                    self.memory.append(page)
                    self.history.append({
                        'type': 'page_fault_replace',
                        'page': page,
                        'replaced_page': replaced_page,
                        'frequency': self.frequency[page],
                        'time': access_time
                    })

                # 更新快表
                if self.use_quick_table:
                    if page not in self.quick_table:
                        if len(self.quick_table) >= min(4, self.memory_size):
                            self.quick_table.pop(0)
                        self.quick_table.append(page)

        self.total_time += access_time
        self.step += 1
        return is_page_fault, replaced_page, access_time
