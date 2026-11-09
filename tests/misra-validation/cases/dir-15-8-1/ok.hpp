#ifndef KV_DIR_15_8_1_OK_HPP
#define KV_DIR_15_8_1_OK_HPP

// Compliant: the hand-written copy assignment tests for self-assignment first.
#include <cstdint>

namespace kv::dir_15_8_1::ok {

class Frame {
 public:
  Frame() = default;
  Frame(const Frame& other) : length_(other.length_) {}
  Frame(Frame&& other) noexcept : length_(other.length_) {}
  Frame& operator=(const Frame& other) & {
    if (this != &other) {
      length_ = other.length_;
    }
    return *this;
  }
  Frame& operator=(Frame&& other) & noexcept {
    if (this != &other) {
      length_ = other.length_;
    }
    return *this;
  }
  ~Frame() {}

  [[nodiscard]] std::uint32_t length() const { return length_; }

 private:
  std::uint32_t length_ = 0U;
};

}  // namespace kv::dir_15_8_1::ok

#endif  // KV_DIR_15_8_1_OK_HPP
