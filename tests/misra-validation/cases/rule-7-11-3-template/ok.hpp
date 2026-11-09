// Compliant: member functions of a class template called by name. A call is not a conversion to
// pointer-to-function; the non-template class below does the same and is the control.
#ifndef KV_RULE_7_11_3_OK_TEMPLATE_HPP
#define KV_RULE_7_11_3_OK_TEMPLATE_HPP

#include <cstdint>

namespace kv::rule_7_11_3::ok_template {

template <typename T>
class Box {
 public:
  explicit Box(T v) noexcept : v_{v} {}
  [[nodiscard]] T get() const noexcept { return value(); }  // member call in a class template

 private:
  [[nodiscard]] T value() const noexcept { return v_; }
  T v_;
};

class Plain {
 public:
  explicit Plain(std::uint32_t v) noexcept : v_{v} {}
  [[nodiscard]] std::uint32_t get() const noexcept { return value(); }  // control: not reported

 private:
  [[nodiscard]] std::uint32_t value() const noexcept { return v_; }
  std::uint32_t v_;
};

inline std::uint32_t use() noexcept { return Box<std::uint32_t>{2U}.get() + Plain{3U}.get(); }

}  // namespace kv::rule_7_11_3::ok_template

#endif  // KV_RULE_7_11_3_OK_TEMPLATE_HPP
