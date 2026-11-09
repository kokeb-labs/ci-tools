// Compliant: a constexpr variable template is const (Rule 6.7.2). The pack reports it once it is
// named with a dependent argument in a template.
#ifndef KV_RULE_6_7_2_OK_VARIABLE_TEMPLATE_HPP
#define KV_RULE_6_7_2_OK_VARIABLE_TEMPLATE_HPP

#include <cstdint>
#include <type_traits>

namespace kv::rule_6_7_2::var_template {

template <typename T>
concept ClassType = std::is_class_v<T>;

template <ClassType>
inline constexpr bool kAlwaysFalse = false;

template <typename Port>
concept HasDelay = requires(Port& port) { port.DelayUs(1U); };

template <typename Port>
void DelayUs(Port& port, std::uint32_t us) noexcept {
  if constexpr (HasDelay<Port>) {
    port.DelayUs(us);
  } else {
    static_assert(kAlwaysFalse<Port>, "the port must implement DelayUs");
  }
}

struct Port {
  void DelayUs(std::uint32_t) noexcept {}
};

inline void Use() noexcept {
  Port port{};
  DelayUs(port, 1U);
}

}  // namespace kv::rule_6_7_2::var_template

#endif  // KV_RULE_6_7_2_OK_VARIABLE_TEMPLATE_HPP
