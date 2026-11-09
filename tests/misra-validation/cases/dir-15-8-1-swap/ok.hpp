// Near miss: copy-and-swap; a self-assignment copies and swaps back.
#ifndef KV_DIR_15_8_1_OK_SWAP_HPP
#define KV_DIR_15_8_1_OK_SWAP_HPP

#include <cstdint>
#include <utility>

namespace kv::dir_15_8_1_swap::ok_swap {

class Frame {
 public:
  Frame() = default;
  Frame(const Frame& other) : length_(other.length_) {}
  Frame(Frame&& other) noexcept : length_(other.length_) {}
  Frame& operator=(const Frame& other) & {
    Frame copy(other);
    std::swap(length_, copy.length_);
    return *this;
  }
  Frame& operator=(Frame&& other) & noexcept {
    std::swap(length_, other.length_);
    return *this;
  }
  ~Frame() {}

  [[nodiscard]] std::uint32_t length() const { return length_; }

 private:
  std::uint32_t length_ = 0U;
};

}  // namespace kv::dir_15_8_1_swap::ok_swap

#endif  // KV_DIR_15_8_1_OK_SWAP_HPP
