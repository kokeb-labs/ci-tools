#ifndef KV_RULE_18_4_1_OK_HPP
#define KV_RULE_18_4_1_OK_HPP

// Compliant: the moves are noexcept (destructors are noexcept by default).
#include <cstdint>

namespace kv::rule_18_4_1::ok {

class Block {
 public:
  Block() = default;
  Block(const Block& other) : size_(other.size_) {}
  Block(Block&& other) noexcept : size_(other.size_) {}
  Block& operator=(const Block& other) & {
    if (this != &other) {
      size_ = other.size_;
    }
    return *this;
  }
  Block& operator=(Block&& other) & noexcept {
    if (this != &other) {
      size_ = other.size_;
    }
    return *this;
  }
  ~Block() {}

  [[nodiscard]] std::uint32_t size() const { return size_; }

 private:
  std::uint32_t size_ = 0U;
};

}  // namespace kv::rule_18_4_1::ok

#endif  // KV_RULE_18_4_1_OK_HPP
