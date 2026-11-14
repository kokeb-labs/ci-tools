// A fixed-capacity ring buffer of bytes (the ru-cmake-matrix self-test fixture).
#pragma once

#include <cstddef>
#include <cstdint>

namespace ring {

class Ring {
 public:
  static constexpr std::size_t kCapacity = 8U;

  bool Push(std::uint8_t value) noexcept;
  bool Pop(std::uint8_t& value) noexcept;
  std::size_t Size() const noexcept { return size_; }

 private:
  std::uint8_t data_[kCapacity] = {};
  std::size_t head_ = 0U;
  std::size_t size_ = 0U;
};

// The configuration the library was built for, e.g. "HOST/NONE".
const char* Configuration() noexcept;

}  // namespace ring
