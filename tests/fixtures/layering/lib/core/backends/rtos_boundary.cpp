// The RTOS boundary: the only file that includes an RTOS header (deviations/boundary-files.yml).
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "core/counter.hpp"

#ifdef ESP_PLATFORM
extern "C" void fx_rtos_yield() { taskYIELD(); }
#endif
