// Near miss: defaulted moves and a plain copy assignment.
#ifndef KV_RULE_18_4_1_OK_DEFAULTED_HPP
#define KV_RULE_18_4_1_OK_DEFAULTED_HPP

#include <cstdint>

namespace kv::rule_18_4_1::ok_defaulted {

class Block {
 public:
  Block() = default;
  Block(const Block&) = default;
  Block(Block&&) noexcept = default;
  Block& operator=(const Block&) & = default;
  Block& operator=(Block&&) & noexcept = default;
  ~Block() = default;

  void swap(Block& other) noexcept {
    const std::uint32_t t = size_;
    size_ = other.size_;
    other.size_ = t;
  }

  [[nodiscard]] std::uint32_t size() const { return size_; }

 private:
  std::uint32_t size_ = 0U;
};

}  // namespace kv::rule_18_4_1::ok_defaulted

#endif  // KV_RULE_18_4_1_OK_DEFAULTED_HPP
