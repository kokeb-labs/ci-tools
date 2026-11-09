// Seeded violation (both): an overrider marked both virtual and override.
#include <cstdint>

namespace kv::rule_13_3_1::bad_both {

class Port {
 public:
  virtual ~Port() = default;
  virtual std::int32_t read() const = 0;
};

class Fake : public Port {
 public:
  virtual std::int32_t read() const override { return 1; }
};

std::int32_t sample(const Port& p) { return p.read(); }

}  // namespace kv::rule_13_3_1::bad_both
