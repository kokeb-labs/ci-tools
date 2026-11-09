// Compliant: a class template member returning a reference into *this is const&-qualified and its
// rvalue form is deleted (Rule 6.8.4). The pack reports the instantiated member.
#ifndef KV_RULE_6_8_4_OK_TEMPLATE_HPP
#define KV_RULE_6_8_4_OK_TEMPLATE_HPP

#include <cstdint>

namespace kv::rule_6_8_4::tmpl {

struct Config {
  std::uint32_t value{0U};
};

template <typename Port>
class Driver {
 public:
  explicit Driver(Port& port) noexcept : port_(port) {}
  [[nodiscard]] const Config& GetConfig() const& noexcept { return config_; }
  void GetConfig() const&& = delete;
  [[nodiscard]] Port& GetPort() const noexcept { return port_; }

 private:
  Port& port_;
  Config config_{};
};

struct NullPort {};

inline std::uint32_t Use() noexcept {
  NullPort port{};
  const Driver<NullPort> driver(port);
  return driver.GetConfig().value;
}

}  // namespace kv::rule_6_8_4::tmpl

#endif  // KV_RULE_6_8_4_OK_TEMPLATE_HPP
