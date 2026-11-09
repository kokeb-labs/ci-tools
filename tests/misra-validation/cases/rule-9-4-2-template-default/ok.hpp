// Compliant: a switch in a class template over the class's own scoped enumeration lists every
// enumerator and ends with default (Rule 9.4.2). The pack reports a missing enumerator.
#ifndef KV_RULE_9_4_2_OK_TEMPLATE_HPP
#define KV_RULE_9_4_2_OK_TEMPLATE_HPP

#include <cstdint>

namespace kv::rule_9_4_2::tmpl {

template <typename Port>
class Driver {
 public:
  explicit Driver(Port& port) noexcept : port_(port) {}
  [[nodiscard]] std::uint32_t Word() const noexcept {
    switch (mode_) {
      case Mode::Manual:
        return 1U;
      case Mode::Auto:
        return 2U;
      case Mode::Unknown:
        break;
      default:
        break;
    }
    return 0U;
  }

 private:
  enum class Mode : std::uint8_t { Unknown, Manual, Auto };
  Port& port_;
  Mode mode_{Mode::Unknown};
};

struct NullPort {};

inline std::uint32_t Use() noexcept {
  NullPort port{};
  const Driver<NullPort> driver(port);
  return driver.Word();
}

}  // namespace kv::rule_9_4_2::tmpl

#endif  // KV_RULE_9_4_2_OK_TEMPLATE_HPP
