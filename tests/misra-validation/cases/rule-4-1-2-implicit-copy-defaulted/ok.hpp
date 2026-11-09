// Compliant: every special member is declared, explicitly defaulted.
#ifndef KV_RULE_4_1_2_IMPLICIT_COPY_DEFAULTED_OK_HPP
#define KV_RULE_4_1_2_IMPLICIT_COPY_DEFAULTED_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_2_implicit_copy_defaulted::ok {

class Buffer {
 public:
  explicit Buffer(std::uint32_t n) : n_(n) {}
  Buffer(const Buffer&) = default;
  Buffer(Buffer&&) noexcept = default;
  Buffer& operator=(const Buffer&) = default;
  Buffer& operator=(Buffer&&) noexcept = default;
  ~Buffer() = default;
  [[nodiscard]] std::uint32_t size() const { return n_; }

 private:
  std::uint32_t n_;
};
inline std::uint32_t clone_size(const Buffer& b) {
  const Buffer c(b);
  return c.size();
}

}  // namespace kv::rule_4_1_2_implicit_copy_defaulted::ok

#endif  // KV_RULE_4_1_2_IMPLICIT_COPY_DEFAULTED_OK_HPP
