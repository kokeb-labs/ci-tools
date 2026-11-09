// Compliant: private members of a class template, a plain one and a member function template,
// both called by a public member.
#ifndef KV_RULE_0_2_4_OK_TEMPLATE_HPP
#define KV_RULE_0_2_4_OK_TEMPLATE_HPP

#include <cstdint>

namespace kv::rule_0_2_4::ok_template {

template <typename Port>
class Driver {
 public:
  [[nodiscard]] std::uint32_t Read(bool ok) const noexcept { return ok ? twice() : fail<std::uint32_t>(); }

 private:
  [[nodiscard]] std::uint32_t twice() const noexcept { return count_ << 1U; }
  template <typename T>
  [[nodiscard]] T fail() const noexcept { return T{}; }
  std::uint32_t count_{1U};
};

inline std::uint32_t use(bool ok) noexcept { return Driver<int>{}.Read(ok); }

}  // namespace kv::rule_0_2_4::ok_template

#endif  // KV_RULE_0_2_4_OK_TEMPLATE_HPP
