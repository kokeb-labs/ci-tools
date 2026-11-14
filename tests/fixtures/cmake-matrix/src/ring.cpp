#include "ring/ring.hpp"

namespace ring {

bool Ring::Push(std::uint8_t value) noexcept {
  if (size_ == kCapacity) {
    return false;
  }
  data_[(head_ + size_) % kCapacity] = value;
  ++size_;
  return true;
}

bool Ring::Pop(std::uint8_t& value) noexcept {
  if (size_ == 0U) {
    return false;
  }
  value = data_[head_];
  head_ = (head_ + 1U) % kCapacity;
  --size_;
  return true;
}

const char* Configuration() noexcept {
#if defined(RING_MCU_ESP32) && defined(RING_RTOS_FREERTOS)
  return "ESP32/FREERTOS";
#elif defined(RING_MCU_STM32F4)
  return "STM32F4";
#else
  return "HOST/NONE";
#endif
}

}  // namespace ring
