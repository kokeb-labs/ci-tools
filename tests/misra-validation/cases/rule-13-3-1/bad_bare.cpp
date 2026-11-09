// Seeded violation (bare): an overrider with neither virtual nor override.
#include <cstdint>

namespace kv::rule_13_3_1::bad_bare {

class Port {
 public:
  virtual ~Port() = default;
  virtual std::int32_t read() const = 0;
};

class Fake : public Port {
 public:
  std::int32_t read() const { return 2; }  // seeded
};

std::int32_t sample(const Port& p) { return p.read(); }

}  // namespace kv::rule_13_3_1::bad_bare
